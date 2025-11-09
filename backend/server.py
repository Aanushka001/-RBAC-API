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
import jwt
import logging
import os

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))
DB_NAME = "Assignment"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(MONGO_URL)
    app.mongodb_client = client
    app.db = client[DB_NAME]
    yield
    client.close()

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
    token = credentials.credentials
    payload = decode_token(token)
    email = payload.get("email")
    role = payload.get("role")
    db = app.db
    collection = db.admins if role == "admin" else db.users
    user = await collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"email": user["email"], "role": role, "user_id": str(user["_id"])}

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
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
    user = await app.db.users.find_one({"email": user_data.email}) or \
           await app.db.admins.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.get("role") == "admin":
        if user_data.password != user["password"]:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        if not verify_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"email": user["email"], "role": user["role"]})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            role=user["role"],
            created_at=user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else str(user["created_at"])
        )
    )

@api_router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(current_user=Depends(get_current_user)):
    tasks = await app.db.tasks.find({"user_id": current_user["user_id"]}).to_list(100)
    for task in tasks:
        task["id"] = str(task["_id"])
        task["created_at"] = task["created_at"].isoformat()
        task["updated_at"] = task["updated_at"].isoformat()
    return tasks

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

@api_router.get("/notes", response_model=List[NoteResponse])
async def get_notes(current_user=Depends(get_current_user)):
    notes = await app.db.notes.find({"user_id": current_user["user_id"]}).to_list(100)
    for note in notes:
        note["id"] = str(note["_id"])
        note["created_at"] = note["created_at"].isoformat()
        note["updated_at"] = note["updated_at"].isoformat()
    return notes

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

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    users = await app.db.users.find().to_list(100)
    for user in users:
        user["id"] = str(user["_id"])
        if isinstance(user["created_at"], datetime):
            user["created_at"] = user["created_at"].isoformat()
    return users

@app.get("/")
async def root():
    return {
        "message": "🚀 FastAPI Assignment API is running",
        "endpoints": [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/tasks",
            "/api/v1/notes",
            "/api/v1/users",
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
