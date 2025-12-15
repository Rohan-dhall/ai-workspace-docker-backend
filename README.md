# 🧠 AI Workspace Backend

AI Workspace Backend is a **lightweight MVP backend** built using **FastAPI** and **SQLite**.  
It provides essential backend capabilities for an AI-powered workspace, including authentication, document management, task tracking, and a simple AI chat assistant.

This project is ideal for **learning**, **demos**, and **small-scale deployments**.

---

## 🚀 Features

### 🔐 Authentication & Authorization
- User registration and login
- Token-based authentication using **HTTP Bearer tokens**
- Role-based access control (**User / Admin**)
- Default admin user created on first run

### 📄 Document Management
- File upload support
- Files stored locally on the server
- UUID-based unique filenames
- File metadata stored in SQLite
- Document listing per user

### ✅ Task Management
- Create tasks manually
- Filter tasks by status
- AI-assisted task creation from chat messages

### 🤖 AI Assistant (Rule-Based)
- Simple conversational responses
- Detects task-related intent
- Automatically creates tasks when triggered
- Logs AI usage for analytics
- **No external ML or LLM dependencies**

### 📊 Admin Capabilities
- View all registered users
- Access AI usage statistics
- Basic platform analytics

### 🗄️ Persistence
- SQLite database
- Automatic table creation on startup

---

## 🧱 Technology Stack

| Component        | Technology |
|------------------|------------|
| Backend          | FastAPI |
| Database         | SQLite |
| Server           | Uvicorn |
| Authentication   | Custom HTTP Bearer Tokens |
| Validation       | Pydantic |
| AI Logic         | Rule-based (internal) |

---

## 🔐 Authentication Details

Authentication is handled using **HTTP Bearer tokens**.

### Login Flow
1. User logs in with username and password
2. API returns an `access_token`
3. Token must be included in all protected requests

### Header Format
Authorization: Bearer <access_token>

> ⚠️ **Note:**  
> - Tokens do **not expire**
> - Tokens are derived from password hashes  
> - This approach is **only for MVP/demo purposes**  
> - **Not recommended for production**

---

## 🤖 AI Capabilities

The built-in AI assistant can:

- Respond to basic conversational inputs
- Detect task-related commands (e.g., "create a task to...")
- Automatically create tasks from chat messages
- Track and log AI interactions for admin analytics

The AI is **fully rule-based** and does **not** use:
- External APIs
- Machine Learning models
- LLMs (ChatGPT, etc.)

---

## 📁 File Uploads

- Files are saved locally on the server
- Each file is renamed using a **UUID**
- File metadata is stored in the database
- No file size limit enforcement
- No virus or malware scanning

> ⚠️ Intended for internal use or demos only

---

## 👑 Admin Access

Admin users can:
- View all registered users
- Monitor AI assistant usage
- Access system-level analytics

### Default Admin
- A default admin user is created automatically on first run
- Credentials can be configured in the source code or environment variables
