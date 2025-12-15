FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ curl
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ /app/
RUN mkdir -p uploads vector_db
EXPOSE 8000
CMD ["python", "main.py"]
