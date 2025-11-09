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
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
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

class Task(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    user_id: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

class TaskCreate(BaseModel):
    title: str
    description: str
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), app=Depends(lambda: app)):
    token = credentials.credentials
    payload = decode_token(token)
    email = payload.get("email")
    role = payload.get("role")
    collection = app.db.admins if role == "admin" else app.db.users
    user = await collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"email": user["email"], "role": role}

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, app=Depends(lambda: app)):
    existing = await app.db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": user_data.email,
        "name": user_data.name,
        "password": hash_password(user_data.password),
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await app.db.users.insert_one(doc)
    token = create_access_token({"email": doc["email"], "role": "user"})
    return Token(access_token=token, token_type="bearer", user=UserResponse(
        id=str(doc.get("_id", "")),
        email=doc["email"],
        name=doc["name"],
        role="user",
        created_at=doc["created_at"]
    ))

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, app=Depends(lambda: app)):
    user = await app.db.users.find_one({"email": user_data.email})
    if not user:
        user = await app.db.admins.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"email": user["email"], "role": user["role"]})
    return Token(access_token=token, token_type="bearer", user=UserResponse(
        id=str(user.get("_id", "")),
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user["created_at"]
    ))

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user=Depends(get_current_user), app=Depends(lambda: app)):
    tasks = await app.db.tasks.find({"user_id": current_user["email"]}).to_list(100)
    return tasks

@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user=Depends(get_current_user), app=Depends(lambda: app)):
    doc = task_data.model_dump()
    doc["user_id"] = current_user["email"]
    doc["created_at"] = datetime.now(timezone.utc)
    doc["updated_at"] = datetime.now(timezone.utc)
    await app.db.tasks.insert_one(doc)
    return doc

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "db": DB_NAME}

@app.get("/")
async def root():
    return {
        "message": "FastAPI Assignment API is running 🚀",
        "available_endpoints": [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/tasks",
            "/api/v1/health"
        ]
    }

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
