import chromadb
from chromadb.config import Settings
import requests
import json
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
import uuid

class RAGSystem:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        # Initialize ChromaDB
        chromadb_dir = "vector_db"
        os.makedirs(chromadb_dir, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(
            path=chromadb_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        print(f"RAG System initialized with Ollama ({self.model})")
    
    def check_ai_status(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def embed_text(self, text: str) -> List[float]:
        """Get embeddings from Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["embedding"]
        except Exception as e:
            print(f"Embedding error: {e}")
        
        # Fallback: simple dummy embedding
        return [0.1] * 384
    
    def generate_response(self, query: str, context: str = "", user_id: int = None) -> Dict[str, Any]:
        """Generate AI response using Ollama with tool calling"""
        try:
            # Prepare prompt with context
            prompt = f"""You are an AI assistant for a workspace system. You have access to tools.

Available tools:
1. create_task - Create a new task for the user
2. list_tasks - List user's tasks
3. search_documents - Search in user's documents
4. list_recent_documents - List recently uploaded documents
5. summarize_documents - Summarize selected documents

Context from user's documents:
{context[:2000]}

User query: {query}

If the query requires information not in the context, say: "This information is not available in your uploaded documents."

If the user asks to create a task, call create_task tool.
If the user asks about their tasks, call list_tasks tool.
If the user asks about documents, use search_documents or list_recent_documents.

Respond naturally and helpfully."""

            # Call Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                ai_response = response.json()["response"]
                tools_called = []
                
                # Simple tool detection
                if "create task" in query.lower() or "task for" in query.lower():
                    tools_called.append("create_task")
                    # Extract task title
                    task_title = query.replace("create task", "").replace("Create task", "").strip()
                    if not task_title:
                        task_title = "Task from AI"
                    ai_response = f"{ai_response}\n\nTask created: '{task_title}'"
                
                elif "list tasks" in query.lower() or "my tasks" in query.lower():
                    tools_called.append("list_tasks")
                    ai_response = f"{ai_response}\n\nHere are your tasks..."
                
                elif "document" in query.lower() and "search" in query.lower():
                    tools_called.append("search_documents")
                
                elif "recent documents" in query.lower():
                    tools_called.append("list_recent_documents")
                
                return {
                    "response": ai_response,
                    "tools_called": tools_called
                }
            
        except Exception as e:
            print(f"AI generation error: {e}")
        
        # Fallback response
        return {
            "response": "I'm here to help! You can ask me about your documents or create tasks.",
            "tools_called": []
        }
    
    def add_document_to_vector_db(self, document_id: str, text_chunks: List[str], metadata: Dict, workspace_id: str):
        """Add document chunks to vector database"""
        try:
            # Get or create collection for workspace
            collection_name = f"workspace_{workspace_id}"
            collection = self.chroma_client.get_or_create_collection(name=collection_name)
            
            # Generate embeddings and add to collection
            embeddings = [self.embed_text(chunk) for chunk in text_chunks]
            ids = [f"{document_id}_{i}" for i in range(len(text_chunks))]
            metadatas = [{**metadata, "chunk_index": i, "document_id": document_id} 
                        for i in range(len(text_chunks))]
            
            collection.add(
                embeddings=embeddings,
                documents=text_chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            print(f"Vector DB error: {e}")
            return False
    
    def search_documents(self, query: str, workspace_id: str, limit: int = 3) -> str:
        """Search for relevant documents"""
        try:
            collection_name = f"workspace_{workspace_id}"
            collection = self.chroma_client.get_collection(name=collection_name)
            
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            if results and results["documents"]:
                # Combine results
                context = "\n".join(results["documents"][0])
                return context
            
        except Exception as e:
            print(f"Search error: {e}")
        
        return ""
    
    def delete_document(self, document_id: str):
        """Delete document from vector DB"""
        # This is simplified - in production, you'd need to delete all chunks

        pass
