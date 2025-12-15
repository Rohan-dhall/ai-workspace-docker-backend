import pypdf
from typing import List
import os
import sys

sys.path.append('/app')

from database import SessionLocal
from models import Document
import uuid

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    
    return text.strip()

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except:
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Chunk text intelligently"""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        
        if i + chunk_size >= len(words):
            break
    
    return chunks

def process_document_async(document_id: str, file_path: str, user_id: int, workspace_id: str):
    """Process document in background"""
    try:
        db = SessionLocal()
        
        print(f"Processing document: {document_id}")
        
        # Extract text based on file type
        text = ""
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.txt'):
            text = extract_text_from_txt(file_path)
        elif file_path.lower().endswith('.md'):
            text = extract_text_from_txt(file_path)
        else:
            text = f"File: {os.path.basename(file_path)}"
        
        # Chunk text
        chunks = chunk_text(text)
        
        print(f"Document {document_id} processed: {len(chunks)} chunks")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"Document processing error: {e}")

        return False

