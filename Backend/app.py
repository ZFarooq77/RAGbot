from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
import time
import signal
import atexit
import shutil
# Import RAG pipeline functions
from utils.ragPipeline import process_with_rag_pipeline, query_with_rag, check_if_chromadb_empty, clear_chromadb

# Load .env and Groq API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("HERE IS GROQ API KEY....", GROQ_API_KEY)

# App setup
app = Flask(__name__)
app.secret_key = 'your-secret-key-for-sessions'  # Change this to a secure secret key
app.permanent_session_lifetime = 3600  # Session expires after 1 hour
CORS(app, supports_credentials=True)

# Ensure uploaded_files directory exists
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global dictionary to track uploaded files per session
session_files = {}

def get_session_folder(session_id):
    """Get or create session-specific folder"""
    session_folder = os.path.join(UPLOAD_FOLDER, f"session_{session_id}")
    os.makedirs(session_folder, exist_ok=True)
    return session_folder

def cleanup_session_files(session_id):
    """Clean up files for a specific session"""
    try:
        session_folder = os.path.join(UPLOAD_FOLDER, f"session_{session_id}")
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
            print(f"🗑️ Cleaned up session folder: {session_folder}")

        # Remove from session tracking
        if session_id in session_files:
            del session_files[session_id]
            print(f"🗑️ Removed session {session_id} from tracking")
    except Exception as e:
        print(f"❌ Error cleaning up session {session_id}: {str(e)}")

def cleanup_all_session_files():
    """Clean up all session files"""
    try:
        # Clean up all session folders
        for session_id in list(session_files.keys()):
            cleanup_session_files(session_id)

        # Also clean up any orphaned session folders
        if os.path.exists(UPLOAD_FOLDER):
            for item in os.listdir(UPLOAD_FOLDER):
                item_path = os.path.join(UPLOAD_FOLDER, item)
                if os.path.isdir(item_path) and item.startswith("session_"):
                    shutil.rmtree(item_path)
                    print(f"🗑️ Cleaned up orphaned folder: {item_path}")
                elif os.path.isfile(item_path):
                    # Clean up any loose files in the main upload folder
                    os.remove(item_path)
                    print(f"🗑️ Cleaned up loose file: {item_path}")
    except Exception as e:
        print(f"❌ Error cleaning up all session files: {str(e)}")

# Cleanup function to clear ChromaDB and session files on app shutdown
def cleanup_chromadb():
    print("🧹 Cleaning up ChromaDB and session files before shutdown...")
    clear_chromadb()
    cleanup_all_session_files()
    print("🗑️ Cleared all session data")

# Register cleanup function to run on app exit
atexit.register(cleanup_chromadb)

# Handle SIGINT (Ctrl+C) and SIGTERM signals
def signal_handler(sig, frame):
    print(f"\n🛑 Received signal {sig}, shutting down gracefully...")
    cleanup_chromadb()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)



@app.route("/upload", methods=["POST"])
def upload_file():
    print("📩 Received upload request")
    print("📎 request.files:", request.files)
    print("📎 request.form:", request.form)
    print("📎 request.content_type:", request.content_type)
    print("📎 request.headers:", dict(request.headers))

    try:
        # Get or create session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session.permanent = True  # Make session permanent (with timeout)
            session_files[session['session_id']] = []
            print(f"🆔 Created new session: {session['session_id']}")
        else:
            print(f"🆔 Using existing session: {session['session_id']}")

        files = request.files.getlist("file")  # 👈 NOTE: Frontend should send 'file'
        print(f"📋 Found {len(files)} files in request")

        if not files:
            print("🚫 No files uploaded - files list is empty")
            return jsonify({"error": "No files uploaded"}), 400

        # Check if files are actually file objects or empty
        valid_files = [f for f in files if f and f.filename != ""]
        print(f"📋 Valid files after filtering: {len(valid_files)}")

        if not valid_files:
            print("🚫 No valid files - all files have empty filenames")
            return jsonify({"error": "No valid files uploaded"}), 400

        file_paths = []
        uploaded_file_info = []

        # Get session-specific folder
        session_folder = get_session_folder(session['session_id'])

        for file in valid_files:
            print(f"📄 Processing file: {file.filename} (type: {file.content_type})")

            # Unique file name in session folder
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(session_folder, filename)
            file.save(file_path)
            print(f"📂 Saved to session folder: {file_path}")
            file_paths.append(file_path)

            # Track file info for this session
            file_info = {
                "original_name": file.filename,
                "saved_path": file_path,
                "upload_time": time.time(),
                "content_type": file.content_type
            }
            uploaded_file_info.append(file_info)
            session_files[session['session_id']].append(file_info)

        if not file_paths:
            print("🚫 No file paths created")
            return jsonify({"error": "No valid files uploaded"}), 400

        print(f"🚀 Starting RAG pipeline with {len(file_paths)} files")
        # Run RAG pipeline
        result = process_with_rag_pipeline(file_paths)
        print(f"✅ RAG pipeline result: {result}")

        if result:
            return jsonify({
                "message": "Files processed successfully",
                "session_id": session['session_id'],
                "uploaded_files": uploaded_file_info
            }), 200
        else:
            return jsonify({"error": "RAG pipeline failed"}), 500

    except Exception as e:
        print("🔥 Exception in /upload:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/query", methods=["POST"])
def query():
    user_query = request.json.get("query")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        answer = query_with_rag(user_query)
        return jsonify({"answer": answer}), 200
    except Exception as e:
        print("🔥 Error in /query:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear_database():
    """Endpoint to manually clear ChromaDB"""
    try:
        result = clear_chromadb()
        if result:
            return jsonify({"message": "ChromaDB cleared successfully"}), 200
        else:
            return jsonify({"error": "Failed to clear ChromaDB"}), 500
    except Exception as e:
        print("🔥 Error in /clear:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/session/clear", methods=["POST"])
def clear_session():
    """Endpoint to clear current session data"""
    try:
        if 'session_id' not in session:
            return jsonify({"message": "No active session to clear"}), 200

        session_id = session['session_id']

        # Clear ChromaDB
        clear_chromadb()

        # Clean up session files
        cleanup_session_files(session_id)

        # Clear session
        session.clear()

        return jsonify({
            "message": "Session cleared successfully",
            "cleared_session_id": session_id
        }), 200
    except Exception as e:
        print("🔥 Error in /session/clear:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/files", methods=["GET"])
def get_session_files():
    """Get list of uploaded files for the current session"""
    try:
        if 'session_id' not in session:
            return jsonify({"files": [], "session_id": None}), 200

        session_id = session['session_id']
        files = session_files.get(session_id, [])

        # Format file info for frontend
        formatted_files = []
        for file_info in files:
            formatted_files.append({
                "name": file_info["original_name"],
                "upload_time": file_info["upload_time"],
                "content_type": file_info["content_type"]
            })

        return jsonify({
            "files": formatted_files,
            "session_id": session_id,
            "total_files": len(formatted_files)
        }), 200
    except Exception as e:
        print("🔥 Error in /files:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/chromadb/status", methods=["GET"])
def get_chromadb_status():
    """Get ChromaDB status and document count"""
    try:
        from utils.ragPipeline import db

        # Get collection info
        collection = db.get()
        total_docs = len(collection['ids'])

        is_empty = total_docs == 0

        return jsonify({
            "is_empty": is_empty,
            "total_documents": total_docs,
            "status": "empty" if is_empty else "has_data",
            "message": f"ChromaDB {'is empty' if is_empty else f'contains {total_docs} documents'}"
        }), 200
    except Exception as e:
        print("🔥 Error in /chromadb/status:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting RAG Chatbot with in-memory ChromaDB...")
    print("📝 Note: ChromaDB data will be cleared when the session ends")
    app.run(debug=True)
    












# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os
# import uuid
# from utils.ragPipeline import process_with_rag_pipeline

# from utils.processFiles import load_and_split_files
# from utils.ragPipeline import get_rag_answer, store_embeddings

# # Load API keys
# load_dotenv()
# OPENAI_API_KEY = os.getenv("GROQ_API_KEY")
# print("HERE IS GROQ API KEY....", os.getenv("GROQ_API_KEY"))

# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = "uploaded_files"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# UPLOAD_FOLDER = "uploaded_files"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/upload", methods=["POST"])
# def upload_file():
#     try:
#         files = request.files.getlist("files")
#         if not files:
#             print("🚫 No files uploaded")
#             return jsonify({"error": "No files uploaded"}), 400

#         file_paths = []
#         for file in files:
#             if file.filename == "":
#                 continue  # skip empty filenames

#             # Generate unique filename
#             filename = f"{uuid.uuid4()}_{file.filename}"
#             file_path = os.path.join(UPLOAD_FOLDER, filename)
#             file.save(file_path)
#             print(f"📂 Saved: {file_path}")
#             file_paths.append(file_path)

#         if not file_paths:
#             return jsonify({"error": "No valid files uploaded"}), 400

#         # Call your RAG pipeline
#         success = process_with_rag_pipeline(file_paths)  # Ensure it accepts a list
#         if success:
#             return jsonify({"message": "Files processed successfully"}), 200
#         else:
#             print("❌ RAG pipeline failed")
#             return jsonify({"error": "RAG pipeline failed"}), 500

#     except Exception as e:
#         print("🔥 Exception in /upload:", str(e))
#         return jsonify({"error": str(e)}), 500


    
# @app.route("/query", methods=["POST"])
# def query():
#     user_query = request.json.get("query")
    
#     if not user_query:
#         return jsonify({"error": "No query provided"}), 400

#     try:
#         result = get_rag_answer(user_query)
#         return jsonify({"answer": result})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(debug=True)
