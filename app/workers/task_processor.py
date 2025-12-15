import time
from typing import Dict, Any
import json

class TaskProcessor:
    """Simple background task processor"""
    
    @staticmethod
    def process_document(document_data: Dict[str, Any]):
        """Process document in background"""
        print(f"Processing document: {document_data.get('filename')}")
        time.sleep(2)  # Simulate processing
        print(f"Document processed: {document_data.get('filename')}")
        return True
    
    @staticmethod
    def create_ai_task(task_data: Dict[str, Any]):
        """Create task from AI request"""
        print(f"Creating AI task: {task_data.get('title')}")
        time.sleep(1)
        print(f"AI task created: {task_data.get('title')}")

        return True
