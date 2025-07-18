# 🤖 RAGbot - Retrieval-Augmented Generation Chatbot

RAGbot is a Retrieval-Augmented Generation (RAG) chatbot built with Python, Flask, ChromaDB, and HuggingFace embeddings. It allows users to upload documents (PDF, DOCX, PPTX, TXT), generates embeddings, and answers queries using LLaMA 4 hosted via Groq API.

---

## 🚀 Features

- 📄 Supports multiple file types: PDF, DOCX, PPTX, TXT
- 🔍 Embeds documents using `all-MiniLM-L6-v2` via HuggingFace
- 🧠 Vector storage and retrieval using ChromaDB (local)
- 💬 LLM-powered answers using Groq’s LLaMA 4 model
- ⚙️ Flask backend with endpoints for file upload and query processing

---

## 📁 Project Structure

RAGbot/
├── Backend/
│ ├── app.py
│ ├── rag_pipeline.py
│ ├── utils/
│ │ ├── ...
│ └── chroma_db/
├── Frontend/
│ ├── components/
│ ├── App.js
│ └── ...
├── .vscode/
│ └── settings.json
├── .env
├── requirements.txt
└── README.md

yaml
Copy
Edit

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ZFarooq77/RAGbot.git
cd RAGbot
2. Create Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate     # On Linux/macOS
venv\Scripts\activate        # On Windows
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Set Environment Variables
Create a .env file in the root directory and add:

env
Copy
Edit
GROQ_API_KEY=your_groq_api_key_here
▶️ Run the Flask Backend
bash
Copy
Edit
cd Backend
python app.py
The API should be available at http://localhost:5000.

🧠 How It Works
User uploads document(s)

Documents are split and embedded using HuggingFace

Embeddings are stored in ChromaDB

When a user asks a question, the top-k relevant chunks are retrieved

A prompt is constructed and sent to LLaMA 4 via Groq API

The model responds with a contextual answer

📦 Technologies Used
Python + Flask – Backend API

LangChain – Document loading, splitting, and chaining

ChromaDB – Local vector database

HuggingFace – Sentence embedding model

Groq API – LLaMA 4-based language model

React.js – Frontend interface
