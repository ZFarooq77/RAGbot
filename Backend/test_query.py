import requests
import json

def test_query():
    # Test query endpoint
    url = "http://localhost:5000/query"
    
    test_queries = [
        "What is deep learning?",
        "Tell me about AI learning roadmap",
        "What are the main topics covered in the documents?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: {query}")
        
        data = {"query": query}
        response = requests.post(url, json=data)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')}")
        else:
            print(f"❌ Query failed!")
            print(f"📝 Error: {response.text}")

if __name__ == "__main__":
    test_query()
