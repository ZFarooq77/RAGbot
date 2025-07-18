from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
import time
# Import RAG pipeline functions
from utils.ragPipeline import process_with_rag_pipeline, query_with_rag, check_if_chromadb_empty

# Load .env and Groq API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("HERE IS GROQ API KEY....", GROQ_API_KEY)

# App setup
app = Flask(__name__)
CORS(app)

# Ensure uploaded_files directory exists
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



@app.route("/upload", methods=["POST"])
def upload_file():
    print("📩 Received upload request")
    print("📎 request.files:", request.files)
    print("📎 request.form:", request.form)
    print("📎 request.content_type:", request.content_type)
    print("📎 request.headers:", dict(request.headers))

    try:
        files = request.files.getlist("file")  # 👈 NOTE: Frontend should send 'file' not 'files'
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
        for file in valid_files:
            print(f"📄 Processing file: {file.filename} (type: {file.content_type})")

            # Unique file name
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            print(f"📂 Saved: {file_path}")
            file_paths.append(file_path)

        if not file_paths:
            print("🚫 No file paths created")
            return jsonify({"error": "No valid files uploaded"}), 400

        print(f"🚀 Starting RAG pipeline with {len(file_paths)} files")
        # Run RAG pipeline
        result = process_with_rag_pipeline(file_paths)
        print(f"✅ RAG pipeline result: {result}")

        if result:
            return jsonify({"message": "Files processed successfully"}), 200
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

if __name__ == "__main__":
    x=0
    while(x<5):
        if(check_if_chromadb_empty() == 0):
            print("Chroma is empty")
        else:
            print("\chroma is not empty")
        x = x+1
        time.sleep(7)
    
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
