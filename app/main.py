from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import uuid
import os
import json
import hashlib
from datetime import datetime
import uvicorn

# Initialize
os.makedirs("uploads", exist_ok=True)
os.makedirs("vector_db", exist_ok=True)
os.makedirs("database", exist_ok=True)

DB_PATH = "database/ai_workspace.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            workspace_id TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_path TEXT,
            file_size INTEGER,
            file_type TEXT,
            status TEXT DEFAULT 'pending',
            metadata TEXT,
            user_id INTEGER,
            workspace_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            due_date TIMESTAMP,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'todo',
            linked_documents TEXT,
            user_id INTEGER,
            created_by_ai BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            message TEXT,
            response TEXT,
            tools_called TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, workspace_id) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@example.com", password_hash, "admin", str(uuid.uuid4()))
        )
        print("✅ Created admin user: admin/admin123")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize database
init_db()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    workspace_id: str
    is_active: bool
    created_at: str

class DocumentUpload(BaseModel):
    filename: str
    content: bytes

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    file_type: str
    status: str
    user_id: int
    created_at: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tools_called: List[str]
    chat_id: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    linked_documents: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    linked_documents: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    due_date: Optional[str]
    priority: str
    status: str
    linked_documents: List[str]
    user_id: int
    created_by_ai: bool
    created_at: str

# Simple AI service
class SimpleAI:
    def chat(self, message: str):
        responses = {
            "hello": "Hello! I'm your AI assistant.",
            "hi": "Hi there! How can I help?",
            "task": "I can help you create tasks.",
            "document": "You can upload documents for me to analyze.",
            "help": "Available: register, login, upload files, create tasks, chat"
        }
        
        for key in responses:
            if key in message.lower():
                return responses[key]
        
        return f"I received: {message}. How can I assist you?"

ai_service = SimpleAI()

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_token(username: str) -> str:
    return hashlib.sha256(f"{username}{datetime.now()}".encode()).hexdigest()

# FastAPI app
app = FastAPI(title="AI Workspace")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Dependency for auth
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Simple token check (in production use JWT)
    cursor.execute("SELECT * FROM users WHERE password_hash = ?", (token,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "role": user[4],
        "workspace_id": user[5]
    }

# ========== AUTH ENDPOINTS ==========
@app.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", 
                  (user.username, user.email))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    password_hash = hash_password(user.password)
    workspace_id = str(uuid.uuid4())
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, workspace_id)
        VALUES (?, ?, ?, ?)
    ''', (user.username, user.email, password_hash, workspace_id))
    
    user_id = cursor.lastrowid
    conn.commit()
    
    # Get created user
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    return UserResponse(
        id=user_data[0],
        username=user_data[1],
        email=user_data[2],
        role=user_data[4],
        workspace_id=user_data[5],
        is_active=bool(user_data[6]),
        created_at=user_data[7]
    )

@app.post("/auth/login")
def login(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data or not verify_password(user.password, user_data[3]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create simple token (password_hash as token for demo)
    return {
        "access_token": user_data[3],  # Using password hash as token
        "token_type": "bearer",
        "user_id": user_data[0],
        "username": user_data[1],
        "role": user_data[4]
    }

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],))
    user_data = cursor.fetchone()
    conn.close()
    
    return UserResponse(
        id=user_data[0],
        username=user_data[1],
        email=user_data[2],
        role=user_data[4],
        workspace_id=user_data[5],
        is_active=bool(user_data[6]),
        created_at=user_data[7]
    )

# ========== DOCUMENT ENDPOINTS ==========
@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Read file
    content = await file.read()
    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO documents (id, filename, file_path, file_size, file_type, user_id, workspace_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (file_id, file.filename, file_path, len(content), 
          file.filename.split('.')[-1] if '.' in file.filename else 'unknown',
          current_user["id"], current_user["workspace_id"]))
    
    conn.commit()
    conn.close()
    
    return DocumentResponse(
        id=file_id,
        filename=file.filename,
        file_size=len(content),
        file_type=file.filename.split('.')[-1] if '.' in file.filename else 'unknown',
        status="pending",
        user_id=current_user["id"],
        created_at=datetime.now().isoformat()
    )

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", 
                  (current_user["id"],))
    docs = cursor.fetchall()
    conn.close()
    
    return [DocumentResponse(
        id=d[0],
        filename=d[1],
        file_size=d[3],
        file_type=d[4],
        status=d[5],
        user_id=d[7],
        created_at=d[9]
    ) for d in docs]

# ========== CHAT ENDPOINTS ==========
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    # Get AI response
    response = ai_service.chat(request.message)
    chat_id = str(uuid.uuid4())
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chats (id, user_id, message, response)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, current_user["id"], request.message, response))
    
    conn.commit()
    conn.close()
    
    # Check if task creation requested
    tools_called = []
    if "task" in request.message.lower() and "create" in request.message.lower():
        tools_called.append("create_task")
        # Extract task title
        words = request.message.lower().split()
        try:
            task_index = words.index("task")
            title = " ".join(words[task_index+1:task_index+4]).title()
            
            # Create task
            task_id = str(uuid.uuid4())
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (id, title, description, user_id, created_by_ai)
                VALUES (?, ?, ?, ?, ?)
            ''', (task_id, title, f"From chat: {request.message}", current_user["id"], True))
            conn.commit()
            conn.close()
            
            response += f"\n\n✅ Task created: '{title}'"
        except:
            pass
    
    return ChatResponse(
        response=response,
        tools_called=tools_called,
        chat_id=chat_id
    )

# ========== TASK ENDPOINTS ==========
@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    task_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (id, title, description, due_date, priority, linked_documents, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (task_id, task.title, task.description, task.due_date, task.priority,
          json.dumps(task.linked_documents), current_user["id"]))
    
    conn.commit()
    
    # Get created task
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task_data = cursor.fetchone()
    conn.close()
    
    return TaskResponse(
        id=task_data[0],
        title=task_data[1],
        description=task_data[2],
        due_date=task_data[3],
        priority=task_data[4],
        status=task_data[5],
        linked_documents=json.loads(task_data[6]) if task_data[6] else [],
        user_id=task_data[7],
        created_by_ai=bool(task_data[8]),
        created_at=task_data[9]
    )

@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [current_user["id"]]
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    query += " ORDER BY created_at DESC"
    cursor.execute(query, tuple(params))
    tasks = cursor.fetchall()
    conn.close()
    
    return [TaskResponse(
        id=t[0],
        title=t[1],
        description=t[2],
        due_date=t[3],
        priority=t[4],
        status=t[5],
        linked_documents=json.loads(t[6]) if t[6] else [],
        user_id=t[7],
        created_by_ai=bool(t[8]),
        created_at=t[9]
    ) for t in tasks]

# ========== ADMIN ENDPOINTS ==========
@app.get("/admin/users")
def admin_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return [{
        "id": u[0],
        "username": u[1],
        "email": u[2],
        "role": u[3],
        "created_at": u[4]
    } for u in users]

@app.get("/admin/ai-usage")
def admin_ai_usage(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM chats")
    total_chats = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE created_by_ai = 1")
    ai_tasks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_chats": total_chats,
        "tasks_created_by_ai": ai_tasks,
        "total_users": total_users,
        "timestamp": datetime.now().isoformat()
    }

# ========== HEALTH & INFO ==========
@app.get("/")
def root():
    return {
        "app": "AI Workspace Backend",
        "version": "1.0",
        "database": "SQLite",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    db_exists = os.path.exists(DB_PATH)
    return {
        "status": "healthy" if db_exists else "degraded",
        "database": db_exists,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 AI Workspace with SQLite Starting...")
    print(f"📁 Database: {DB_PATH}")
    uvicorn.run(app, host="0.0.0.0", port=8000)