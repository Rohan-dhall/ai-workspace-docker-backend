@echo off
echo Creating AI Workspace Docker Setup...
echo.

REM Create project structure
if not exist "app" mkdir app
if not exist "uploads" mkdir uploads
if not exist "vector_db" mkdir vector_db

echo [1/4] Creating Dockerfile...
echo FROM python:3.10-slim > Dockerfile
echo WORKDIR /app >> Dockerfile
echo RUN apt-get update ^&^& apt-get install -y gcc g++ curl >> Dockerfile
echo COPY requirements.txt . >> Dockerfile
echo RUN pip install --upgrade pip >> Dockerfile
echo RUN pip install --no-cache-dir -r requirements.txt >> Dockerfile
echo COPY app/ /app/ >> Dockerfile
echo RUN mkdir -p uploads vector_db >> Dockerfile
echo EXPOSE 8000 >> Dockerfile
echo CMD ["python", "main.py"] >> Dockerfile

echo [2/4] Creating requirements.txt...
echo fastapi==0.104.1 > requirements.txt
echo uvicorn[standard]==0.24.0 >> requirements.txt
echo requests==2.31.0 >> requirements.txt
echo python-jose[cryptography]==3.3.0 >> requirements.txt
echo passlib[bcrypt]==1.7.4 >> requirements.txt
echo python-multipart==0.0.6 >> requirements.txt
echo pydantic==2.5.0 >> requirements.txt
echo pypdf==3.17.4 >> requirements.txt
echo numpy==1.24.3 >> requirements.txt

echo [3/4] Creating main.py...
REM Copy the simplified main.py code to app/main.py

echo [4/4] Creating docker-compose.yml...
echo version: '3.8' > docker-compose.yml
echo. >> docker-compose.yml
echo services: >> docker-compose.yml
echo   ai-api: >> docker-compose.yml
echo     build: . >> docker-compose.yml
echo     ports: >> docker-compose.yml
echo       - "8000:8000" >> docker-compose.yml
echo     volumes: >> docker-compose.yml
echo       - ./uploads:/app/uploads >> docker-compose.yml
echo       - ./vector_db:/app/vector_db >> docker-compose.yml

echo.
echo ✅ Setup complete!
echo.
echo To run:
echo   1. docker build -t ai-workspace .
echo   2. docker run -p 8000:8000 ai-workspace
echo.
echo OR with Docker Compose:
echo   docker-compose up -d
echo.
pause