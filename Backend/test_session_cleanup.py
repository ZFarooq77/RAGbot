import requests
import os
import time

def test_session_cleanup():
    """Test session cleanup functionality"""
    base_url = "http://localhost:5000"
    
    # Create test file
    test_content = "This is a test document for session cleanup testing."
    test_file_path = "test_cleanup.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    print("🧪 Testing session cleanup functionality...")
    
    # Create a session
    session = requests.Session()
    
    # Step 1: Upload file
    print("\n📤 Step 1: Upload file")
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        response = session.post(f"{base_url}/upload", files=files)
    
    print(f"📊 Upload status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
    
    # Step 2: Check files exist
    print("\n📁 Step 2: Check files exist")
    response = session.get(f"{base_url}/files")
    if response.status_code == 200:
        data = response.json()
        print(f"📁 Files in session: {len(data.get('files', []))}")
    
    # Step 3: Check ChromaDB has data
    print("\n🔍 Step 3: Check ChromaDB status")
    response = session.get(f"{base_url}/chromadb/status")
    if response.status_code == 200:
        data = response.json()
        print(f"📊 ChromaDB documents: {data.get('total_documents', 0)}")
    
    # Step 4: Check uploaded_files directory
    print("\n📂 Step 4: Check uploaded_files directory")
    upload_dir = "uploaded_files"
    if os.path.exists(upload_dir):
        session_folders = [item for item in os.listdir(upload_dir) if item.startswith("session_")]
        print(f"📁 Session folders: {len(session_folders)}")
    
    # Step 5: Clear session
    print("\n🗑️ Step 5: Clear session")
    response = session.post(f"{base_url}/session/clear")
    print(f"📊 Clear status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data.get('message', 'Session cleared')}")
    
    # Step 6: Verify cleanup
    print("\n✅ Step 6: Verify cleanup")
    
    # Check ChromaDB is empty
    response = session.get(f"{base_url}/chromadb/status")
    if response.status_code == 200:
        data = response.json()
        print(f"📊 ChromaDB after cleanup: {data.get('total_documents', 0)} documents")
    
    # Check files are gone
    response = session.get(f"{base_url}/files")
    if response.status_code == 200:
        data = response.json()
        print(f"📁 Files after cleanup: {len(data.get('files', []))}")
    
    # Check directory is cleaned
    if os.path.exists(upload_dir):
        session_folders = [item for item in os.listdir(upload_dir) if item.startswith("session_")]
        print(f"📂 Session folders after cleanup: {len(session_folders)}")
    
    # Cleanup test file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"\n🗑️ Cleaned up test file: {test_file_path}")

if __name__ == "__main__":
    test_session_cleanup()
