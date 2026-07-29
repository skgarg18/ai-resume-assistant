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

    One JSON object is written per retrieval request.

    This log is workflow-agnostic and can be used for
    Candidate Lookup, Candidate Search, Comparison,
    Ranking, etc.
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
                "candidate_name": chunk.get(
                    "candidate_name"
                ),

                "resume_id": chunk.get(
                    "resume_id"
                ),

                "chunk_index": chunk.get(
                    "chunk_index"
                ),

                "cosine_similarity": round(
                    chunk.get(
                        "cosine_similarity",
                        0,
                    ),
                    4,
                ),

                "chunk_text": chunk.get(
                    "chunk_text"
                ),
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