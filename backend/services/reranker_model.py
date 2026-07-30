import gc
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

# Global lazy loading to prevent reloading model on every request
_RERANKER_MODEL = None


def get_reranker_model() -> CrossEncoder:
    global _RERANKER_MODEL
    if _RERANKER_MODEL is None:
        # High accuracy cross-encoder for semantic + entity reranking
        _RERANKER_MODEL = CrossEncoder("BAAI/bge-reranker-base")
    return _RERANKER_MODEL


def preload_reranker_model():
    """Forces reranker to load into memory at app startup."""
    get_reranker_model() #[cite: 6]