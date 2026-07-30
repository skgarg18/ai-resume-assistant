import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from config.constants import LOG_DIR

LOG_FILE = LOG_DIR / "retrieval_scores.jsonl"


def log_retrieval_results(
    *,
    workflow: str,
    session_id: str,
    query: str,
    retrieved_chunks: list,
):
    """
    Store retrieval results for offline evaluation.

    Supports both legacy vector retrieval and Hybrid + Reranked retrieval metrics.
    One JSON object is written per retrieval request.
    """

    log_entry = {
        "timestamp": datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).isoformat(),

        "workflow": workflow,

        "session_id": session_id,

        "query": query,

        "retrieved_chunk_count": len(
            retrieved_chunks
        ),

        "retrieved_chunks": [
            {
                "candidate_name": chunk.get("candidate_name"),

                "resume_id": chunk.get("resume_id"),

                "chunk_index": chunk.get("chunk_index"),

                # Cross-Encoder Rerank Logit Score (Primary ranking metric)
                "rerank_score": (
                    round(chunk["rerank_score"], 4)
                    if chunk.get("rerank_score") is not None
                    else None
                ),

                # Original Vector Cosine Similarity
                "cosine_similarity": (
                    round(chunk["cosine_similarity"], 4)
                    if chunk.get("cosine_similarity") is not None
                    else None
                ),

                # Positions before Reciprocal Rank Fusion (RRF)
                "vector_rank": chunk.get("vector_rank"),

                "bm25_rank": chunk.get("bm25_rank"),

                "chunk_text": chunk.get("chunk_text"),
            }

            for chunk in retrieved_chunks
        ],
    }

    try:
        with open(
            LOG_FILE,
            "a",
            encoding="utf-8",
        ) as f:

            json.dump(
                log_entry,
                f,
                ensure_ascii=False,
                indent=None,
            )

            f.write("\n")

    except Exception as e:
        # Logging failures should never break the workflow.
        print(
            f"Failed writing retrieval log: {e}"
        )