"""
Service responsible for Hybrid Search (BM25 + Vector), RRF Fusion, 
Post-Rerank Candidate Deduplication, Cross-Encoder Reranking, 
and Dynamic Parameter Scaling.
"""
import math
from typing import List, Dict, Any, Optional
from collections import defaultdict
from rank_bm25 import BM25Okapi

from database.active_repository import resume_chunks_repo
from services.reranker_model import get_reranker_model
from utils.log_utils import get_logger


def _sigmoid(x: float) -> float:
    """Converts unbounded cross-encoder logits to a 0.0 - 1.0 probability score."""
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _resolve_dynamic_retrieval_params(
    total_chunks: int, unique_resumes: int
) -> tuple[int, float]:
    """
    Dynamically select retrieval metrics based on the volume of uploaded resumes.
    Returns: (top_n_fusion, min_rerank_score)
    """
    top_n_fusion = max(15, min(total_chunks, unique_resumes * 3))
    min_rerank_score = 0.0001  # Extremely light noise filter

    return top_n_fusion, min_rerank_score


def perform_hybrid_candidate_search(
    session_id: str,
    query_text: str,
    query_embedding: list[float],
) -> Optional[List[Dict[str, Any]]]:
    """
    Executes hybrid search and cross-encoder reranking over resume chunks for a session.
    Guarantees candidate coverage by applying sigmoid scoring and candidate diversity.
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

        unique_resumes = len(
            set(m.get("resume_id") for m in all_metas if m and m.get("resume_id"))
        )
        total_chunks = len(all_ids)

        # 2. Resolve Search Metrics
        top_n_fusion, min_rerank_score = _resolve_dynamic_retrieval_params(
            total_chunks=total_chunks, unique_resumes=unique_resumes
        )

        logger.info(
            "Dynamic Metrics Resolved | Resumes={} | Chunks={} | FusionCap={} | MinRerank={}",
            unique_resumes,
            total_chunks,
            top_n_fusion,
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

        # 3. Dense Vector Search
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

        all_fused_ids = sorted(
            rrf_scores.keys(), key=lambda doc_id: rrf_scores[doc_id], reverse=True
        )

        # Group RRF chunks by candidate
        candidate_rrf_chunks = defaultdict(list)
        for doc_id in all_fused_ids:
            meta = doc_map[doc_id]["metadata"]
            cand_key = meta.get("resume_id") or meta.get("candidate_name") or "unknown"
            candidate_rrf_chunks[cand_key].append(doc_id)

        # Guarantee at least 1 chunk per candidate enters cross-encoder pool
        fused_ids = []
        selected_set = set()

        for cand_key, chunks in candidate_rrf_chunks.items():
            if chunks:
                first_chunk = chunks[0]
                fused_ids.append(first_chunk)
                selected_set.add(first_chunk)

        RRF_MAX_PER_CANDIDATE = 3
        rrf_candidate_counts = {
            cand_key: 1 for cand_key in candidate_rrf_chunks.keys()
        }

        for doc_id in all_fused_ids:
            if doc_id in selected_set:
                continue

            meta = doc_map[doc_id]["metadata"]
            cand_key = meta.get("resume_id") or meta.get("candidate_name") or "unknown"
            count = rrf_candidate_counts.get(cand_key, 0)

            if count < RRF_MAX_PER_CANDIDATE:
                fused_ids.append(doc_id)
                selected_set.add(doc_id)
                rrf_candidate_counts[cand_key] = count + 1

            if len(fused_ids) >= top_n_fusion:
                break

        if not fused_ids:
            return []

        # 6. Cross-Encoder Reranking
        reranker = get_reranker_model()
        pairs = [[query_text, doc_map[doc_id]["chunk_text"]] for doc_id in fused_ids]
        raw_rerank_scores = reranker.predict(pairs)

        # Normalize raw logits to probabilities via Sigmoid
        normalized_scores = [_sigmoid(float(s)) for s in raw_rerank_scores]

        scored_candidates = sorted(
            zip(fused_ids, normalized_scores), key=lambda x: x[1], reverse=True
        )

        # 7. Post-Rerank Candidate Deduplication & Output
        FINAL_MAX_PER_CANDIDATE = 2
        final_candidate_counts = {}
        final_results = []

        for doc_id, score_float in scored_candidates:
            if score_float < min_rerank_score:
                continue

            meta = doc_map[doc_id]["metadata"]
            cand_key = meta.get("resume_id") or meta.get("candidate_name") or "unknown"

            current_count = final_candidate_counts.get(cand_key, 0)
            if current_count >= FINAL_MAX_PER_CANDIDATE:
                continue

            final_candidate_counts[cand_key] = current_count + 1

            doc_info = doc_map[doc_id]
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