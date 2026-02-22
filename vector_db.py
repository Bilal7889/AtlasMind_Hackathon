"""
Vector database operations using ChromaDB
"""

from typing import List
import chromadb
from sentence_transformers import SentenceTransformer
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL

# Initialize clients
chroma_client = chromadb.Client()
embedding_model = SentenceTransformer(EMBEDDING_MODEL)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks


def store_in_vector_db(content_id: str, text: str):
    """
    Store text chunks in ChromaDB (works for video transcript or PDF content).

    Args:
        content_id: Unique id (e.g. YouTube video_id or pdf_<hash>)
        text: Full text to chunk and embed

    Returns:
        ChromaDB collection object or None if failed
    """
    try:
        collection_name = f"content_{content_id}"
        try:
            chroma_client.delete_collection(collection_name)
        except:
            pass
        collection = chroma_client.create_collection(collection_name)

        chunks = chunk_text(text)
        embeddings = embedding_model.encode(chunks).tolist()
        collection.add(
            embeddings=embeddings,
            documents=chunks,
            ids=[f"chunk_{i}" for i in range(len(chunks))]
        )
        print(f"Stored {len(chunks)} chunks in vector DB")
        return collection
    except Exception as e:
        print(f"Vector DB error: {e}")
        return None


def semantic_search(query: str, collection, top_k: int = 3) -> str:
    """
    Search for relevant chunks using semantic similarity
    
    Args:
        query: Search query
        collection: ChromaDB collection
        top_k: Number of top results to return
    
    Returns:
        Concatenated relevant text chunks
    """
    if not collection:
        return ""
    try:
        query_embedding = embedding_model.encode([query]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=top_k)
        return "\n".join(results['documents'][0])
    except:
        return ""
