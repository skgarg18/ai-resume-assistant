"""
Service responsible for Hybrid Search (BM25 + Vector), RRF Fusion, 
Cross-Encoder Reranking, and Dynamic Parameter Scaling.
"""
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi

from database.active_repository import resume_chunks_repo
from services.reranker_model import get_reranker_model
from utils.log_utils import get_logger


def _resolve_dynamic_retrieval_params(
    total_chunks: int, unique_resumes: int
) -> tuple[int, float, float]:
    """
    Dynamically select retrieval metrics based on the volume of uploaded resumes.
    Returns: (top_n_fusion, max_score_delta, min_rerank_score)
    """
    if unique_resumes <= 5:
        # Small Pool: High recall, rerank almost all candidates
        top_n_fusion = min(10, total_chunks)
        max_score_delta = 0.6
        min_rerank_score = -0.5
    elif unique_resumes <= 20:
        # Medium Pool: Balanced precision and candidate filtering
        top_n_fusion = min(20, total_chunks)
        max_score_delta = 0.8
        min_rerank_score = -0.5
    else:
        # Large Pool (20+ resumes): Strict precision, cap CPU reranker work
        top_n_fusion = 20
        max_score_delta = 0.5
        min_rerank_score = 0.0

    return top_n_fusion, max_score_delta, min_rerank_score


def perform_hybrid_candidate_search(
    session_id: str,
    query_text: str,
    query_embedding: list[float],
) -> Optional[List[Dict[str, Any]]]:
    """
    Executes hybrid search and cross-encoder reranking over resume chunks for a session.
    """
    logger = get_logger()

    try:
        # 1. Fetch Corpus Documents via Repository
        all_chunks = resume_chunks_repo.get_all_session_chunks(session_id)
        all_ids = all_chunks.get("ids", [])
        all_docs = all_chunks.get("documents", [])
        all_metas = all_chunks.get("metadatas", [])

        if not all_ids or not all_docs:
            logger.info("No chunks found in collection for session: {}", session_id)
            return []

        # Count unique resumes and total chunks
        unique_resumes = len(
            set(m.get("resume_id") for m in all_metas if m and m.get("resume_id"))
        )
        total_chunks = len(all_ids)

        # 2. Resolve Search Metrics Dynamically
        top_n_fusion, max_score_delta, min_rerank_score = _resolve_dynamic_retrieval_params(
            total_chunks=total_chunks, unique_resumes=unique_resumes
        )

        logger.info(
            "Dynamic Metrics Resolved | Resumes={} | Chunks={} | FusionCap={} | ScoreDelta={} | MinRerank={}",
            unique_resumes,
            total_chunks,
            top_n_fusion,
            max_score_delta,
            min_rerank_score,
        )

        doc_map = {
            all_ids[i]: {
                "id": all_ids[i],
                "chunk_text": all_docs[i],
                "metadata": all_metas[i] if all_metas else {},
            }
            for i in range(len(all_ids))
        }

        # 3. Dense Vector Search via Repository
        vector_results = resume_chunks_repo.query_vector_nearest_neighbors(
            session_id=session_id,
            query_embedding=query_embedding,
            n_results=total_chunks,
        )

        vector_ids = vector_results.get("ids", [[]])[0]
        vector_distances = vector_results.get("distances", [[]])[0]
        vector_ranks = {doc_id: rank for rank, doc_id in enumerate(vector_ids)}

        # 4. Sparse BM25 Keyword Search
        tokenized_corpus = [doc.lower().split() for doc in all_docs]
        tokenized_query = query_text.lower().split()

        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(tokenized_query)

        sorted_bm25_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )
        bm25_ranks = {
            all_ids[idx]: rank for rank, idx in enumerate(sorted_bm25_indices)
        }

        # 5. Hybrid Rank Fusion (RRF)
        rrf_k = 60
        rrf_scores = {}
        candidate_ids = set(vector_ids).union(set(all_ids))

        for doc_id in candidate_ids:
            v_rank = vector_ranks.get(doc_id, 1000)
            b_rank = bm25_ranks.get(doc_id, 1000)
            rrf_scores[doc_id] = (1.0 / (rrf_k + v_rank)) + (1.0 / (rrf_k + b_rank))

        fused_ids = sorted(
            rrf_scores.keys(), key=lambda doc_id: rrf_scores[doc_id], reverse=True
        )[:top_n_fusion]

        if not fused_ids:
            return []

        # 6. Cross-Encoder Reranking
        reranker = get_reranker_model()
        pairs = [[query_text, doc_map[doc_id]["chunk_text"]] for doc_id in fused_ids]
        rerank_scores = reranker.predict(pairs)

        scored_candidates = sorted(
            zip(fused_ids, rerank_scores), key=lambda x: x[1], reverse=True
        )
        top_score = float(scored_candidates[0][1])

        # 7. Dynamic Cutoff Filtering
        final_results = []
        for doc_id, score in scored_candidates:
            score_float = float(score)

            if score_float < min_rerank_score or (top_score - score_float) > max_score_delta:
                continue

            doc_info = doc_map[doc_id]
            meta = doc_info["metadata"]
            v_dist = vector_distances[vector_ranks[doc_id]] if doc_id in vector_ranks else 1.0

            final_results.append({
                "id": doc_id,
                "resume_id": meta.get("resume_id"),
                "candidate_name": meta.get("candidate_name"),
                "chunk_index": meta.get("chunk_index"),
                "chunk_text": doc_info["chunk_text"],
                "rerank_score": score_float,
                "cosine_similarity": 1.0 - v_dist,
                "bm25_rank": bm25_ranks.get(doc_id),
                "vector_rank": vector_ranks.get(doc_id),
            })

        logger.info(
            "Retrieved {} chunk(s) dynamically for {} resume(s).",
            len(final_results),
            unique_resumes,
        )

        return final_results

    except Exception as e:
        logger.exception("Error during perform_hybrid_candidate_search: {}", e)
        return None