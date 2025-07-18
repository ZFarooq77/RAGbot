import requests
import os

def test_file_upload():
    # Test file upload
    url = "http://localhost:5000/upload"
    
    # Use an existing file from the uploaded_files directory
    test_file_path = "uploaded_files/020137ea-bb7d-48fa-ba99-e4adc49825a4_AI_Learning_Roadmap_8_Weeks.pdf"
    
    if not os.path.exists(test_file_path):
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    print(f"📤 Testing upload with file: {test_file_path}")
    
    with open(test_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    print(f"📊 Response status: {response.status_code}")
    print(f"📊 Response body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Upload successful!")
    else:
        print("❌ Upload failed!")

if __name__ == "__main__":
    test_file_upload()
