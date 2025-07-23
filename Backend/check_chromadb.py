from utils.ragPipeline import check_if_chromadb_empty, db

def check_chromadb_status():
    print("🔍 Checking ChromaDB status...")
    
    # Method 1: Use existing function
    result = check_if_chromadb_empty()
    if result == 0:
        print("✅ ChromaDB is EMPTY")
    else:
        print("📚 ChromaDB has data")
    
    # Method 2: Direct check with more details
    try:
        collection = db.get()
        total_docs = len(collection['ids'])
        
        print(f"📊 Total documents: {total_docs}")
        
        if total_docs > 0:
            print(f"📄 Document IDs (first 5): {collection['ids'][:5]}")
            if collection.get('metadatas'):
                print(f"📋 Sample metadata: {collection['metadatas'][0] if collection['metadatas'] else 'None'}")
        else:
            print("🗂️ No documents found in ChromaDB")
            
    except Exception as e:
        print(f"❌ Error checking ChromaDB: {str(e)}")

if __name__ == "__main__":
    check_chromadb_status()
