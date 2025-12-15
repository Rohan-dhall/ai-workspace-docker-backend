import requests
import json
import time
import uuid
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_test(name, success, message=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"   {message}")

def test_health():
    """Test 1: Health Check"""
    print("\n" + "="*60)
    print("🏥 TEST 1: HEALTH CHECK")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", True, f"Status: {data.get('status')}")
            return True
        else:
            print_test("Health Check", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_system_info():
    """Test 2: System Info"""
    print("\n" + "="*60)
    print("⚙️ TEST 2: SYSTEM INFO")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/system", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("System Info", True, 
                      f"App: {data.get('app', 'Unknown')}, "
                      f"AI Model: {data.get('ai_model', 'Unknown')}")
            return True
        else:
            print_test("System Info", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("System Info", False, f"Error: {str(e)}")
        return False

def test_register():
    """Test 3: User Registration"""
    print("\n" + "="*60)
    print("👤 TEST 3: USER REGISTRATION")
    print("="*60)
    
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": "test123"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            # Your API returns token directly or in response?
            token = data.get("token")
            if token:
                print_test("User Registration", True, 
                          f"User: {username}, Token received: {token[:20]}...")
                return username, "test123", token
            else:
                # Some APIs return token in response body
                print_test("User Registration", True, 
                          f"User: {username}, Response: {data}")
                return username, "test123", None
        else:
            print_test("User Registration", False, 
                      f"Status: {response.status_code}, Response: {response.text}")
            return None, None, None
    except Exception as e:
        print_test("User Registration", False, f"Error: {str(e)}")
        return None, None, None

def test_chat():
    """Test 4: Chat with AI"""
    print("\n" + "="*60)
    print("🤖 TEST 4: CHAT WITH AI")
    print("="*60)
    
    # Test 1: Basic chat
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Hello, who are you?"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", str(data))
            print_test("Basic Chat", True, 
                      f"AI Response: {ai_response[:100]}...")
            return True
        else:
            print_test("Basic Chat", False, 
                      f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test("Basic Chat", False, f"Error: {str(e)}")
        return False

def test_ai_task_creation():
    """Test 5: AI Task Creation"""
    print("\n" + "="*60)
    print("🔧 TEST 5: AI TASK CREATION")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Create a task for me to study AI concepts"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", str(data))
            
            # Check if task was created
            task_keywords = ["task", "created", "create", "todo", "✅"]
            has_task = any(keyword in ai_response.lower() for keyword in task_keywords)
            
            print_test("AI Task Creation", has_task, 
                      f"Response: {ai_response[:100]}...")
            return has_task
        else:
            print_test("AI Task Creation", False, 
                      f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("AI Task Creation", False, f"Error: {str(e)}")
        return False

def test_upload():
    """Test 6: Document Upload"""
    print("\n" + "="*60)
    print("📄 TEST 6: DOCUMENT UPLOAD")
    print("="*60)
    
    # Create a test file
    test_content = b"""Artificial Intelligence and Machine Learning
    
    Artificial Intelligence (AI) is the simulation of human intelligence in machines.
    Machine Learning (ML) is a subset of AI that enables systems to learn from data.
    Deep Learning uses neural networks for complex pattern recognition.
    
    This document is for testing the AI workspace system."""
    
    # Save to file
    test_file_path = "test_document.txt"
    with open(test_file_path, "wb") as f:
        f.write(test_content)
    
    try:
        # Your API expects "file" parameter (not "filename")
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(
                f"{BASE_URL}/upload",
                files=files,
                timeout=10
            )
        
        # Clean up test file
        os.remove(test_file_path)
        
        if response.status_code == 200:
            data = response.json()
            print_test("Document Upload", True, 
                      f"Success! ID: {data.get('id', 'N/A')}, "
                      f"Filename: {data.get('filename', 'N/A')}")
            return data.get("id")
        else:
            print_test("Document Upload", False, 
                      f"Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print_test("Document Upload", False, f"Error: {str(e)}")
        # Clean up test file if it exists
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        return None

def test_document_listing():
    """Test 7: Document Listing"""
    print("\n" + "="*60)
    print("📁 TEST 7: DOCUMENT LISTING")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                count = len(data)
                print_test("List Documents", True, f"Found {count} document(s)")
                return True
            elif isinstance(data, dict) and "documents" in data:
                count = len(data["documents"])
                print_test("List Documents", True, f"Found {count} document(s)")
                return True
            else:
                print_test("List Documents", True, f"Response: {data}")
                return True
        else:
            print_test("List Documents", False, 
                      f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Documents", False, f"Error: {str(e)}")
        return False

def test_task_management():
    """Test 8: Task Management"""
    print("\n" + "="*60)
    print("✅ TEST 8: TASK MANAGEMENT")
    print("="*60)
    
    # Create task
    try:
        response = requests.post(
            f"{BASE_URL}/tasks",
            json={
                "title": "Complete AI Assignment",
                "description": "Test all endpoints and document functionality"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("id")
            print_test("Create Task", True, 
                      f"Task created: {data.get('title', 'N/A')}")
        else:
            print_test("Create Task", False, 
                      f"Status: {response.status_code}, Response: {response.text}")
            task_id = None
    except Exception as e:
        print_test("Create Task", False, f"Error: {str(e)}")
        task_id = None
    
    # List tasks
    try:
        response = requests.get(f"{BASE_URL}/tasks", timeout=5)
        
        if response.status_code == 200:
            tasks = response.json()
            if isinstance(tasks, list):
                count = len(tasks)
                print_test("List Tasks", True, f"Found {count} task(s)")
            elif isinstance(tasks, dict):
                print_test("List Tasks", True, f"Response: {tasks}")
            else:
                print_test("List Tasks", True, f"Tasks endpoint working")
            return True
        else:
            print_test("List Tasks", False, 
                      f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Tasks", False, f"Error: {str(e)}")
        return False

def test_full_rag_workflow():
    """Test 9: Full RAG Workflow"""
    print("\n" + "="*60)
    print("🧠 TEST 9: FULL RAG WORKFLOW")
    print("="*60)
    
    # First upload a document
    print("Step 1: Uploading test document...")
    test_content = b"""Natural Language Processing (NLP) is a field of AI that helps computers understand human language.
    Computer Vision enables machines to interpret visual information.
    Reinforcement Learning is about agents learning from rewards and punishments."""
    
    test_file_path = "test_rag_doc.txt"
    with open(test_file_path, "wb") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_rag_doc.txt", f, "text/plain")}
            upload_response = requests.post(
                f"{BASE_URL}/upload",
                files=files,
                timeout=10
            )
        
        os.remove(test_file_path)
        
        if upload_response.status_code != 200:
            print_test("RAG Workflow - Upload", False, "Failed to upload document")
            return False
        
        # Wait for document processing
        print("Step 2: Waiting for document processing...")
        time.sleep(3)
        
        # Chat about the document content
        print("Step 3: Chatting about document content...")
        chat_response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "What is Natural Language Processing?"},
            timeout=10
        )
        
        if chat_response.status_code == 200:
            data = chat_response.json()
            ai_response = data.get("response", str(data))
            
            # Check if response mentions NLP or related terms
            nlp_keywords = ["natural language", "nlp", "language processing", "human language"]
            has_nlp_content = any(keyword in ai_response.lower() for keyword in nlp_keywords)
            
            print_test("RAG Context Retrieval", has_nlp_content, 
                      f"Response: {ai_response[:150]}...")
            return has_nlp_content
        else:
            print_test("RAG Context Retrieval", False, "Chat failed")
            return False
            
    except Exception as e:
        print_test("RAG Workflow", False, f"Error: {str(e)}")
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 AI WORKSPACE ASSIGNMENT - COMPLETE TEST")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Run all tests
    test_results = {}
    
    # Test 1: Health Check
    test_results["Health Check"] = test_health()
    
    # Test 2: System Info
    test_results["System Info"] = test_system_info()
    
    # Test 3: User Registration
    username, password, token = test_register()
    test_results["User Registration"] = bool(username)
    
    # Test 4: Chat with AI
    test_results["AI Chat"] = test_chat()
    
    # Test 5: AI Task Creation
    test_results["AI Task Creation"] = test_ai_task_creation()
    
    # Test 6: Document Upload
    doc_id = test_upload()
    test_results["Document Upload"] = bool(doc_id)
    
    # Test 7: Document Listing
    test_results["Document Listing"] = test_document_listing()
    
    # Test 8: Task Management
    test_results["Task Management"] = test_task_management()
    
    # Test 9: RAG Workflow
    test_results["RAG Workflow"] = test_full_rag_workflow()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, success in test_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Score: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉")
    elif passed >= total * 0.7:
        print("\n👍 GOOD! Most functionality is working.")
        print("   Review the failed tests above.")
    else:
        print(f"\n⚠️  Needs improvement. {total - passed} test(s) failed.")
    
    print("="*60)

if __name__ == "__main__":
    main()