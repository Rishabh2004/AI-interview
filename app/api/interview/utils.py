import os
import tempfile
from typing import Dict, Any
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.db.memory import add_memory, retrieve_memories
from app.core.config import get_settings

settings = get_settings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

def get_loader(file_ext: str, path: str):
    if file_ext == ".pdf":
        return PyPDFLoader(path)
    elif file_ext in [".docx", ".doc"]:
        return Docx2txtLoader(path)
    elif file_ext in [".txt", ".rtf"]:
        return TextLoader(path)
    return None

async def process_resume(file_content: bytes, filename: str, user_id: str) -> Dict[str, Any]:
    """Functionally process a resume file and store chunks in Mem0"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name

    try:
        file_ext = os.path.splitext(filename)[1].lower()
        loader = get_loader(file_ext, temp_path)
        
        if not loader:
            os.unlink(temp_path)
            return {"status": "error", "message": f"Unsupported file format: {file_ext}"}

        documents = loader.load()
        chunks = text_splitter.split_documents(documents)

        # Store metadata about the document
        # await add_memory(
        #     user_id=user_id,
        #     message=f"RESUME METADATA: File: {filename}, Type: {file_ext}, Total chunks: {len(chunks)}",
        #     metadata={"source": "resume_metadata", "filename": filename}
        # )

        # Store each chunk in Mem0
        for i, chunk in enumerate(chunks):
            chunk_text = f"RESUME CHUNK {i+1}/{len(chunks)}: {chunk.page_content}"
            metadata = {
                "source": "resume",
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "page_number": getattr(chunk, "metadata", {}).get("page", "unknown")
            }

            await add_memory(
                user_id=user_id,
                message=chunk_text,
                metadata=metadata
            )

        os.unlink(temp_path)
        
        return {
            "status": "success",
            "message": f"Resume processed successfully for user {user_id}",
            "user_id": user_id,
            "chunks_stored": len(chunks)
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return {"status": "error", "message": f"Error processing resume: {str(e)}"}