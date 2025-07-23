import os
import requests
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredPowerPointLoader
from langchain.schema import Document

# Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Embeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize ChromaDB (in-memory, no persistence)
db = Chroma(embedding_function=embedding_model)

# Manual call to Groq API
def call_groq_llama(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        print(f"🔥 Groq API HTTP Error: {e}")
        print(f"🔥 Response content: {response.text}")
        raise e
    except Exception as e:
        print(f"🔥 Groq API Error: {e}")
        raise e


def store_embeddings(file_paths):
    print(f"🔍 store_embeddings called with {len(file_paths)} file paths: {file_paths}")
    documents = []
    for file_path in file_paths:
        print(f"📄 Processing file: {file_path}")
        ext = file_path.lower()
        if ext.endswith(".pdf"):
            print(f"📄 Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
        elif ext.endswith(".docx"):
            print(f"📄 Loading DOCX: {file_path}")
            loader = Docx2txtLoader(file_path)
        elif ext.endswith(".pptx"):
            print(f"📄 Loading PPTX: {file_path}")
            loader = UnstructuredPowerPointLoader(file_path)
        elif ext.endswith(".txt"):
            print(f"📄 Loading TXT: {file_path}")
            loader = TextLoader(file_path)
        else:
            print(f"⚠️ Unsupported file type: {file_path}")
            continue

        try:
            docs = loader.load()
            print(f"✅ Loaded {len(docs)} documents from {file_path}")
            documents.extend(docs)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {str(e)}")
            continue

    print(f"📚 Total documents loaded: {len(documents)}")
    if not documents:
        print("❌ No documents to process")
        return False

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks")

    try:
        db.add_documents(chunks)
        print(f"✅ Successfully stored {len(chunks)} chunks to ChromaDB")
        return True
    except Exception as e:
        print(f"❌ Error storing to ChromaDB: {str(e)}")
        return False


def process_with_rag_pipeline(file_paths):
    try:
        return store_embeddings(file_paths)
    except Exception as e:
        print("❌ Failed in RAG pipeline:", str(e))
        return False


def query_with_rag(query):
    # Retrieve relevant documents
    docs = db.similarity_search(query, k=3)
    if not docs:
        return "📂 Please upload documents so I can answer your question."

    # Construct context
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"Use the following documents to answer the question:\n\n{context}\n\nQuestion: {query}"

    try:
        response = call_groq_llama(prompt)
        return response.strip()
    except Exception as e:
        return f"❌ Error calling Groq API: {str(e)}"






def check_if_chromadb_empty():
    collection = db.get()
    print(f"Total documents in ChromaDB: {len(collection['ids'])}")
    if (len(collection["ids"]) == 0):
        return 0
    else:
        return 1

def clear_chromadb():
    """Clear all documents from ChromaDB"""
    try:
        # Get all document IDs
        collection = db.get()
        if collection['ids']:
            # Delete all documents
            db.delete(ids=collection['ids'])
            print(f"🗑️ Cleared {len(collection['ids'])} documents from ChromaDB")
        else:
            print("🗑️ ChromaDB is already empty")
        return True
    except Exception as e:
        print(f"❌ Error clearing ChromaDB: {str(e)}")
        return False


# # utils/ragPipeline.py

# from langchain_community.vectorstores import Chroma
# from langchain.chains import RetrievalQA
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.llms.base import LLM
# from typing import Optional, List
# import requests
# import os
# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import shutil
# from langchain.vectorstores import Chroma


# persist_directory = os.path.join(os.getcwd(), "chroma_db")


# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# def store_embeddings(documents):
#     if not documents:
#         print("❌ No documents to embed.")
#         return
#     print("✅ Documents received")
    
#     # Danger: Deletes everything in chroma_db
#     if os.path.exists(persist_directory):
#         shutil.rmtree(persist_directory)
#         print("🗑️ Existing ChromaDB deleted.")
#     vectordb = Chroma.from_documents(documents, embedding_model, persist_directory=persist_directory)
#     vectordb.persist()
#     print("✅ Embeddings stored to disk.")

# class GroqLLM(LLM):
#     def __init__(self, api_key: str, model_name: str):
#         self.api_key = api_key
#         self.model_name = model_name

#     @property
#     def _llm_type(self) -> str:
#         return "groq"

#     def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
#         response = requests.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers={
#                 "Authorization": f"Bearer {self.api_key}",
#                 "Content-Type": "application/json"
#             },
#             json={
#                 "model": self.model_name,
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.2
#             }
#         )

#         result = response.json()
#         return result['choices'][0]['message']['content']

# def get_rag_answer(query):
#     api_key = os.getenv("GROQ_API_KEY")
#     model = "meta-llama/llama-4-scout-17b-16e-instruct"

#     vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
    
#     # Check if DB has docs
#     if vectorstore._collection.count() == 0:
#         print("📂 ChromaDB is empty.")
#         return "📂 Please upload documents so I can answer your question."

#     retriever = vectorstore.as_retriever()
#     llm = GroqLLM(api_key=api_key, model_name=model)

#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=retriever,
#         return_source_documents=False
#     )

#     try:
#         response = qa_chain.run(query)
#         print("✅ RAG response generated:", response)
#         return response
#     except Exception as e:
#         print("🔥 Error while generating RAG answer:", str(e))
#         return "❌ Failed to generate answer."



# def process_with_rag_pipeline(file_paths):
#     try:
#         all_docs = []

#         for path in file_paths:
#             ext = os.path.splitext(path)[1].lower()

#             if ext == ".pdf":
#                 loader = PyPDFLoader(path)
#                 documents = loader.load()
#                 print(f"📄 Loaded {len(documents)} pages from {path}")
#             else:
#                 print(f"⚠️ Unsupported file format: {path}")
#                 continue

#             # Split long text into chunks
#             splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#             chunks = splitter.split_documents(documents)
#             print(f"✂️ Split into {len(chunks)} chunks")

#             all_docs.extend(chunks)

#         if not all_docs:
#             print("🚫 No valid documents to process.")
#             return False

#         # Store in Chroma with persistence
#         vectorstore = Chroma.from_documents(
#             documents=all_docs,
#             embedding=embedding_model,
#             persist_directory=CHROMA_DIR
#         )
#         vectorstore.persist()
#         print(f"✅ Stored {len(all_docs)} chunks to ChromaDB at '{CHROMA_DIR}'")
#         return True

#     except Exception as e:
#         print("🔥 Error in RAG pipeline:", str(e))
#         return False








# from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings # Note: This is the specific new package for OpenAI classes
# from langchain.chains import RetrievalQA
# from langchain_openai import OpenAI

# import os

# persist_directory = "db"

# import os
# from dotenv import load_dotenv
# load_dotenv()

# from langchain_openai import OpenAIEmbeddings

# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("❌ OPENAI_API_KEY is not set!")

# embedding = OpenAIEmbeddings(api_key=api_key)



# def store_embeddings(documents):
#     vectordb = Chroma.from_documents(documents, embedding, persist_directory=persist_directory)
#     vectordb.persist()


# def get_rag_answer(query):
#     openai_key = os.getenv("OPENAI_API_KEY")
#     embedding = OpenAIEmbeddings(api_key=openai_key)

#     vectorstore = Chroma(persist_directory="db", embedding_function=embedding)
#     retriever = vectorstore.as_retriever()

#     llm = OpenAI(api_key=openai_key, temperature=0)

#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=retriever,
#         return_source_documents=False
#     )

#     return qa_chain.run(query)
