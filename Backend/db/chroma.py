import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# === Configuration ===
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def check_chroma_db():
    print("📦 Checking ChromaDB at:", CHROMA_PATH)

    # 1. Directory check
    if os.path.exists(CHROMA_PATH):
        print("✅ Directory exists.")
    else:
        print("❌ Directory does NOT exist.")
        return

    # 2. Write permission check
    if os.access(CHROMA_PATH, os.W_OK):
        print("✅ Directory is writable.")
    else:
        print("❌ Directory is NOT writable.")

    # 3. List files
    files = os.listdir(CHROMA_PATH)
    print("📁 Files in directory:")
    for f in files:
        print("  -", f)

    # 4. Check expected files
    expected = {"chroma-collections.parquet", "chroma-embeddings.parquet", "index"}
    present = set(files)
    missing = expected - present
    if missing:
        print(f"⚠️ Missing expected files: {', '.join(missing)}")
    else:
        print("✅ All expected files found.")

    # 5. Load vector store and check document count
    try:
        print("🔍 Loading vector store...")
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        count = vectordb._collection.count()
        print(f"📊 Total documents in vector store: {count}")
    except Exception as e:
        print("❌ Failed to load Chroma VectorStore:", str(e))


if __name__ == "__main__":
    check_chroma_db()









#- to delete a persistant db 
# import chromadb
# import shutil
# import os

# # If you used a persistent directory
# CHROMA_PATH = "chroma_db"

# # Delete the chroma folder entirely if it exists
# if os.path.exists(CHROMA_PATH):
#     shutil.rmtree(CHROMA_PATH)
#     print(f"✅ Deleted ChromaDB folder: {CHROMA_PATH}")
# else:
#     print("⚠️ No persistent chroma_db directory found.")

# # OPTIONAL: Clear default chroma path too, just in case
# DEFAULT_CHROMA_PATH = "chromadb"
# if os.path.exists(DEFAULT_CHROMA_PATH):
#     shutil.rmtree(DEFAULT_CHROMA_PATH)
#     print(f"✅ Deleted default ChromaDB folder: {DEFAULT_CHROMA_PATH}")










# import chromadb
# chroma_client = chromadb.Client()
# collection = chroma_client.create_collection(name="my_collection")
# collection.add(
#     ids=["id1", "id2"],
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges"
#     ]
# )
# results = collection.query(
#     query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )
# print(results)
# {
#   'documents': [[
#       'This is a document about pineapple',
#       'This is a document about oranges'
#   ]],
#   'ids': [['id1', 'id2']],
#   'distances': [[1.0404009819030762, 1.243080496788025]],
#   'uris': None,
#   'data': None,
#   'metadatas': [[None, None]],
#   'embeddings': None,
# }
