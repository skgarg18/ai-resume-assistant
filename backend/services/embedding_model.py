"""
Service for loading and running the BAAI/bge-base-en-v1.5 embedding model.
"""
from typing import Optional, List
from sentence_transformers import SentenceTransformer

_EMBEDDING_MODEL: Optional[SentenceTransformer] = None
MODEL_NAME = "BAAI/bge-base-en-v1.5"


def get_embedding_model() -> SentenceTransformer:
    """
    Lazy loader for embedding model. Ensures weights load only once into RAM.
    """
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        # Load the BGE model
        _EMBEDDING_MODEL = SentenceTransformer(MODEL_NAME)
    return _EMBEDDING_MODEL


def encode_query(query: str) -> List[float]:
    """
    Encodes search queries. BGE models achieve higher accuracy when query 
    prompts are prefixed with the BGE retrieval instruction.
    """
    model = get_embedding_model()
    # BGE recommendation for search queries
    instruction = "Represent this sentence for searching relevant passages: "
    full_query = f"{instruction}{query}"
    
    embedding = model.encode(
        full_query,
        normalize_embeddings=True
    )
    return embedding.tolist()


def encode_documents(texts: List[str]) -> List[List[float]]:
    """
    Encodes resume text chunks into normalized vector embeddings.
    """
    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False
    )
    return embeddings.tolist()