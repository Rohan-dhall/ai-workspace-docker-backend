AI Workspace Backend

AI Workspace Backend is a lightweight backend application built using FastAPI and SQLite. It provides core backend functionality for an AI-powered workspace, including user authentication, document management, task tracking, and a basic AI chat assistant.

This project is designed as an MVP backend suitable for learning, demos, and small-scale deployments.

Features

User registration and login

Token-based authentication using HTTP Bearer tokens

Role-based access control (User / Admin)

Document upload and listing

Task creation and task filtering

AI-powered chat assistant (rule-based)

AI-assisted task creation from chat messages

Admin analytics and user management

SQLite database for persistence

Technology Stack

Backend Framework: FastAPI

Database: SQLite

Server: Uvicorn

Authentication: Custom Bearer Token

AI Logic: Simple rule-based AI

Data Validation: Pydantic

Authentication

Authentication is handled using HTTP Bearer tokens.

On login, the API returns an access_token

This token must be sent with every protected request:

Authorization: Bearer <access_token>


Note: Tokens do not expire and are based on password hashes. This is intended only for MVP/demo purposes.

AI Capabilities

The backend includes a basic AI assistant that:

Responds to simple conversational messages

Detects task-related messages

Automatically creates tasks when triggered

Logs AI tool usage for analytics

The AI is currently rule-based and does not use any external ML or LLM services.

File Uploads

Files are stored locally on the server

Each file is saved with a unique UUID-based name

File metadata is stored in the database

No file size limits or virus scanning are implemented

Admin Access

Admin users can:

View all registered users

Access AI usage statistics

A default admin user is created automatically on first run.
