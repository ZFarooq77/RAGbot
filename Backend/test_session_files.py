import requests
import os

def test_session_file_management():
    base_url = "http://localhost:5000"
    
    # Create a session
    session = requests.Session()
    
    print("🧪 Testing session-based file management...")
    
    # Test 1: Upload a file
    print("\n📤 Test 1: Upload a file")
    test_file_path = "test_file.txt"
    
    if os.path.exists(test_file_path):
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = session.post(f"{base_url}/upload", files=files)
        
        print(f"📊 Upload response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful! Session ID: {data.get('session_id', 'N/A')}")
        else:
            print(f"❌ Upload failed: {response.text}")
    else:
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    # Test 2: Check files in session
    print("\n📋 Test 2: Check files in session")
    response = session.get(f"{base_url}/files")
    print(f"📊 Files response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"📁 Files in session: {len(data.get('files', []))}")
        print(f"🆔 Session ID: {data.get('session_id', 'N/A')}")
    
    # Test 3: Check uploaded_files directory structure
    print("\n📂 Test 3: Check directory structure")
    upload_dir = "uploaded_files"
    if os.path.exists(upload_dir):
        items = os.listdir(upload_dir)
        session_folders = [item for item in items if item.startswith("session_")]
        print(f"📁 Session folders found: {len(session_folders)}")
        for folder in session_folders:
            folder_path = os.path.join(upload_dir, folder)
            if os.path.isdir(folder_path):
                files_in_session = os.listdir(folder_path)
                print(f"  📁 {folder}: {len(files_in_session)} files")
    
    # Test 4: Clear session
    print("\n🗑️ Test 4: Clear session")
    response = session.post(f"{base_url}/session/clear")
    print(f"📊 Clear response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Session cleared: {data.get('message', 'N/A')}")
    
    # Test 5: Check directory after cleanup
    print("\n📂 Test 5: Check directory after cleanup")
    if os.path.exists(upload_dir):
        items = os.listdir(upload_dir)
        session_folders = [item for item in items if item.startswith("session_")]
        print(f"📁 Session folders remaining: {len(session_folders)}")

if __name__ == "__main__":
    test_session_file_management()
