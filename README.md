# AI Workspace Backend Assignment

Complete implementation of the AI Workspace Backend assignment using Ollama Mistral (local).

## 🚀 Features

✅ **Authentication & Workspace Isolation**
- JWT-based authentication
- Workspace isolation for user data
- User roles (user/admin)

✅ **Knowledge Hub - Document Upload & Indexing**
- Upload PDF/TXT/MD files
- Automatic text extraction
- Intelligent chunking
- Vector embeddings with Ollama
- Local storage (no AWS S3)

✅ **AI Assistant - RAG + Tool Calling**
- RAG with Ollama Mistral
- Document search and retrieval
- AI tool calling (create_task, list_tasks, etc.)
- Conversation history

✅ **Task Management**
- Manual task creation
- AI-generated tasks
- Task CRUD operations
- Priority and status management

✅ **Admin APIs**
- User management
- AI usage statistics
- Document reprocessing

## 📦 Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite (instead of PostgreSQL)
- **Vector DB**: ChromaDB
- **AI Model**: Ollama Mistral (local, no API keys)
- **Storage**: Local filesystem (instead of AWS S3)
- **Authentication**: JWT
- **Container**: Docker + Docker Compose

## 🛠️ Setup & Installation

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM for Ollama

### Quick Start

1. **Clone and navigate to project**
```bash
git clone <repo-url>
cd ai-assignment