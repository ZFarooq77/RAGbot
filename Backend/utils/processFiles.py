from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

def load_and_split_files(file_paths):
    documents = []

    for path in file_paths:
        suffix = Path(path).suffix.lower()
        if suffix == ".pdf":
            loader = PyPDFLoader(path)
        elif suffix == ".docx":
            loader = Docx2txtLoader(path)
        elif suffix == ".pptx":
            loader = UnstructuredPowerPointLoader(path)
        else:
            continue

        docs = loader.load()
        documents.extend(docs)

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)
