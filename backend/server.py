from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from enum import Enum
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from bson import ObjectId
import jwt
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))
DB_NAME = "Assignment"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGO_URL)
    app.mongodb_client = client
    app.db = client[DB_NAME]
    logger.info("Database connection established")
    yield
    client.close()
    logger.info("Database connection closed")

app = FastAPI(title="Assignment API", lifespan=lifespan)
api_router = APIRouter(prefix="/api/v1")

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskCreate(BaseModel):
    title: str
    description: str
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    user_id: str
    created_at: str
    updated_at: str

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str]
    user_id: str
    created_at: str
    updated_at: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = decode_token(token)
        email = payload.get("email")
        role = payload.get("role")
        
        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        db = app.db
        collection = db.admins if role == "admin" else db.users
        user = await collection.find_one({"email": email})
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return {
            "email": user["email"], 
            "role": role, 
            "user_id": str(user["_id"])
        }
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def validate_object_id(id: str) -> ObjectId:
    if not id or id == "undefined":
        raise HTTPException(status_code=400, detail="Invalid ID provided")
    
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    return ObjectId(id)

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    existing = await app.db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    doc = {
        "email": user_data.email,
        "name": user_data.name,
        "password": hash_password(user_data.password),
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    }
    result = await app.db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    token = create_access_token({"email": doc["email"], "role": "user"})
    
    logger.info(f"User registered successfully: {user_data.email}")
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(doc["_id"]),
            email=doc["email"],
            name=doc["name"],
            role="user",
            created_at=doc["created_at"].isoformat()
        )
    )

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    logger.info(f"Login attempt for email: {user_data.email}")
    
    user = await app.db.users.find_one({"email": user_data.email}) or await app.db.admins.find_one({"email": user_data.email})
    if not user:
        logger.warning(f"Login failed: User not found - {user_data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.get("role") == "admin":
        if user_data.password != user["password"]:
            logger.warning(f"Login failed: Invalid password for admin - {user_data.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        if not verify_password(user_data.password, user["password"]):
            logger.warning(f"Login failed: Invalid password for user - {user_data.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"email": user["email"], "role": user["role"]})
    created_at = user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"])
    
    logger.info(f"Login successful: {user_data.email}")
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            role=user["role"],
            created_at=created_at
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    db = app.db.admins if current_user["role"] == "admin" else app.db.users
    user = await db.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"])
    )

@api_router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(current_user=Depends(get_current_user)):
    tasks = await app.db.tasks.find({"user_id": current_user["user_id"]}).to_list(100)
    for task in tasks:
        task["id"] = str(task["_id"])
        task["created_at"] = task["created_at"].isoformat() if isinstance(task["created_at"], datetime) else str(task["created_at"])
        task["updated_at"] = task["updated_at"].isoformat() if isinstance(task["updated_at"], datetime) else str(task["updated_at"])
    return tasks

@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user=Depends(get_current_user)):
    obj_id = validate_object_id(task_id)
    
    task = await app.db.tasks.find_one({"_id": obj_id, "user_id": current_user["user_id"]})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["id"] = str(task["_id"])
    task["created_at"] = task["created_at"].isoformat() if isinstance(task["created_at"], datetime) else str(task["created_at"])
    task["updated_at"] = task["updated_at"].isoformat() if isinstance(task["updated_at"], datetime) else str(task["updated_at"])
    return task

@api_router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, current_user=Depends(get_current_user)):
    doc = task_data.model_dump()
    doc["user_id"] = current_user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc)
    doc["updated_at"] = datetime.now(timezone.utc)
    result = await app.db.tasks.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()
    return doc

@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_data: TaskUpdate, current_user=Depends(get_current_user)):
    obj_id = validate_object_id(task_id)
    
    existing_task = await app.db.tasks.find_one({"_id": obj_id, "user_id": current_user["user_id"]})
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await app.db.tasks.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    updated_task = await app.db.tasks.find_one({"_id": obj_id})
    updated_task["id"] = str(updated_task["_id"])
    updated_task["created_at"] = updated_task["created_at"].isoformat() if isinstance(updated_task["created_at"], datetime) else str(updated_task["created_at"])
    updated_task["updated_at"] = updated_task["updated_at"].isoformat() if isinstance(updated_task["updated_at"], datetime) else str(updated_task["updated_at"])
    
    return updated_task

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user=Depends(get_current_user)):
    obj_id = validate_object_id(task_id)
    
    result = await app.db.tasks.delete_one({"_id": obj_id, "user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}

@api_router.get("/notes", response_model=List[NoteResponse])
async def get_notes(current_user=Depends(get_current_user)):
    notes = await app.db.notes.find({"user_id": current_user["user_id"]}).to_list(100)
    for note in notes:
        note["id"] = str(note["_id"])
        note["created_at"] = note["created_at"].isoformat() if isinstance(note["created_at"], datetime) else str(note["created_at"])
        note["updated_at"] = note["updated_at"].isoformat() if isinstance(note["updated_at"], datetime) else str(note["updated_at"])
    return notes

@api_router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, current_user=Depends(get_current_user)):
    obj_id = validate_object_id(note_id)
    
    note = await app.db.notes.find_one({"_id": obj_id, "user_id": current_user["user_id"]})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["id"] = str(note["_id"])
    note["created_at"] = note["created_at"].isoformat() if isinstance(note["created_at"], datetime) else str(note["created_at"])
    note["updated_at"] = note["updated_at"].isoformat() if isinstance(note["updated_at"], datetime) else str(note["updated_at"])
    return note

@api_router.post("/notes", response_model=NoteResponse)
async def create_note(note_data: NoteCreate, current_user=Depends(get_current_user)):
    doc = note_data.model_dump()
    doc["user_id"] = current_user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc)
    doc["updated_at"] = datetime.now(timezone.utc)
    result = await app.db.notes.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()
    return doc

@api_router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_data: NoteUpdate, current_user=Depends(get_current_user)):
    obj_id = validate_object_id(note_id)
    
    existing_note = await app.db.notes.find_one({"_id": obj_id, "user_id": current_user["user_id"]})
    if not existing_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await app.db.notes.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    updated_note = await app.db.notes.find_one({"_id": obj_id})
    updated_note["id"] = str(updated_note["_id"])
    updated_note["created_at"] = updated_note["created_at"].isoformat() if isinstance(updated_note["created_at"], datetime) else str(updated_note["created_at"])
    updated_note["updated_at"] = updated_note["updated_at"].isoformat() if isinstance(updated_note["updated_at"], datetime) else str(updated_note["updated_at"])
    
    return updated_note

@api_router.delete("/notes/{note_id}")
async def delete_note(note_id: str, current_user=Depends(get_current_user)):
    obj_id = validate_object_id(note_id)
    
    result = await app.db.notes.delete_one({"_id": obj_id, "user_id": current_user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"message": "Note deleted successfully"}

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users = await app.db.users.find().to_list(100)
    for user in users:
        user["id"] = str(user["_id"])
        user["created_at"] = user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"])
    return users

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    obj_id = validate_object_id(user_id)
    
    if current_user["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = await app.db.users.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await app.db.tasks.delete_many({"user_id": user_id})
    await app.db.notes.delete_many({"user_id": user_id})
    
    logger.info(f"User {user_id} deleted by admin {current_user['email']}")
    return {"message": "User deleted successfully"}

@api_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user=Depends(get_current_user)):
    db = app.db.admins if current_user["role"] == "admin" else app.db.users
    user = await db.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"])
    )

@api_router.put("/profile", response_model=UserResponse)
async def update_profile(user_data: UserUpdate, current_user=Depends(get_current_user)):
    db = app.db.admins if current_user["role"] == "admin" else app.db.users
    
    if user_data.email and user_data.email != current_user["email"]:
        existing_user = await db.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    await db.update_one(
        {"email": current_user["email"]},
        {"$set": update_data}
    )
    
    updated_user = await db.find_one({"email": user_data.email or current_user["email"]})
    
    if user_data.email and user_data.email != current_user["email"]:
        logger.info(f"User {current_user['email']} updated email to {user_data.email}")
    
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        name=updated_user["name"],
        role=updated_user["role"],
        created_at=updated_user["created_at"].isoformat() if isinstance(updated_user["created_at"], datetime) else str(updated_user["created_at"])
    )

@api_router.put("/profile/password")
async def change_password(old_password: str, new_password: str, current_user=Depends(get_current_user)):
    if current_user["role"] == "admin":
        admin = await app.db.admins.find_one({"email": current_user["email"]})
        if not admin or admin["password"] != old_password:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        await app.db.admins.update_one(
            {"email": current_user["email"]},
            {"$set": {"password": new_password}}
        )
    else:
        user = await app.db.users.find_one({"email": current_user["email"]})
        if not user or not verify_password(old_password, user["password"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        await app.db.users.update_one(
            {"email": current_user["email"]},
            {"$set": {"password": hash_password(new_password)}}
        )
    
    logger.info(f"Password changed for user: {current_user['email']}")
    return {"message": "Password updated successfully"}

@app.get("/")
async def root():
    return {
        "message": "🚀 FastAPI Assignment API is running", 
        "endpoints": [
            "/api/v1/auth/register", 
            "/api/v1/auth/login", 
            "/api/v1/auth/me",
            "/api/v1/tasks", 
            "/api/v1/notes", 
            "/api/v1/users", 
            "/api/v1/profile"
        ]
    }

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*", "http://localhost:3000", "http://127.0.0.1:3000"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)