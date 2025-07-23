import requests

def test_files_endpoint():
    # Test files endpoint
    url = "http://localhost:5000/files"
    
    print("🔍 Testing files endpoint...")
    
    response = requests.get(url)
    
    print(f"📊 Response status: {response.status_code}")
    print(f"📊 Response body: {response.text}")
    
    if response.status_code == 200:
        print("✅ Files endpoint working!")
    else:
        print("❌ Files endpoint failed!")

if __name__ == "__main__":
    test_files_endpoint()
