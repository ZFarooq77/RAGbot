import requests
import os

def test_upload_and_query():
    """Test the complete upload and query flow"""
    base_url = "http://localhost:5000"
    
    # Create a test file
    test_content = """
    This is a test document for the RAG chatbot.
    It contains information about artificial intelligence and machine learning.
    AI is transforming various industries including healthcare, finance, and technology.
    Machine learning algorithms can learn from data and make predictions.
    """
    
    test_file_path = "test_document.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    print("🧪 Testing complete upload and query flow...")
    
    # Create a session
    session = requests.Session()
    
    # Test 1: Upload file
    print("\n📤 Step 1: Upload file")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = session.post(f"{base_url}/upload", files=files)
        
        print(f"📊 Upload status: {response.status_code}")
        print(f"📊 Upload response: {response.text}")
        
        if response.status_code != 200:
            print("❌ Upload failed, stopping test")
            return
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test 2: Check ChromaDB status
    print("\n🔍 Step 2: Check ChromaDB status")
    try:
        response = session.get(f"{base_url}/chromadb/status")
        print(f"📊 ChromaDB status: {response.status_code}")
        print(f"📊 ChromaDB response: {response.text}")
    except Exception as e:
        print(f"❌ ChromaDB status error: {e}")
    
    # Test 3: Query the uploaded document
    print("\n❓ Step 3: Query the document")
    try:
        query_data = {"query": "What is artificial intelligence?"}
        response = session.post(f"{base_url}/query", json=query_data)
        
        print(f"📊 Query status: {response.status_code}")
        print(f"📊 Query response: {response.text}")
        
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    # Test 4: Check session files
    print("\n📁 Step 4: Check session files")
    try:
        response = session.get(f"{base_url}/files")
        print(f"📊 Files status: {response.status_code}")
        print(f"📊 Files response: {response.text}")
    except Exception as e:
        print(f"❌ Files error: {e}")
    
    # Cleanup
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"\n🗑️ Cleaned up test file: {test_file_path}")

if __name__ == "__main__":
    test_upload_and_query()
