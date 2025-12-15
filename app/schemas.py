from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# ========== USER SCHEMAS ==========
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    workspace_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== DOCUMENT SCHEMAS ==========
class DocumentBase(BaseModel):
    filename: str

class DocumentUpload(BaseModel):
    filename: str
    content: bytes

class DocumentResponse(DocumentBase):
    id: str
    file_size: int
    file_type: str
    status: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== CHAT SCHEMAS ==========
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tools_called: Optional[List[str]] = []
    chat_id: str

# ========== TASK SCHEMAS ==========
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = "medium"
    linked_documents: Optional[List[str]] = []

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    linked_documents: Optional[List[str]] = None

class TaskResponse(TaskBase):
    id: str
    status: str
    user_id: int
    created_by_ai: bool
    created_at: datetime
    
    class Config:
        from_attributes = True