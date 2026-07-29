from collections import defaultdict
from time import perf_counter

from fastapi import HTTPException

from database.active_repository import (
    resume_chunks_repo,
    chat_hist_repo,
)

from services.embedding_model import get_embedding_model

from utils.log_utils import get_logger
from utils.llm_usage_log_utils import log_llm_usage
from utils.log_chunk_retrival_utils import log_retrieval_results

from langchain_chains.chat_workflow_chains.candidate_search_workflow_chain import (
    candidate_search_chain
)

def build_candidate_search_response(
    query: str,
    matches: list,
) -> dict:
    """
    Build recruiter-friendly response from structured
    candidate search results without total count or CSS margin bloat.
    """

    if not matches:
        return {
            "content":f"No candidates were found matching:\n\n**\"{query}\"**",
            "candidates":[]
            }

    lines = ["**Matching Candidates:**\n"]

    candidates = []

    for candidate in matches:
        # Candidate header
        lines.append(f"**{candidate.candidate_name}**")
        
        # Match significance on the very next line
        reason = getattr(candidate, "match_reason", None)
        if reason:
            lines.append(f"**Match Significance:** {reason.strip()}\n")
        
        candidates.append(
            {
                "id" : candidate.resume_id,
                "match_significance" : reason or ""
            }
        )

    return {
        "content" : "\n".join(lines).strip(),
        "candidates" : candidates
        }




async def candidate_search_workflow(
    session_id: str,
    query: str,
):
    """
    Handles recruiter search queries such as:

    - Who knows Python?
    - Who is AWS certified?
    - Who worked at Microsoft?
    - Who has Kubernetes experience?
    """

    logger = get_logger()

    workflow_start = perf_counter()

    try:

        #
        # ----------------------------------------------------
        # Generate query embedding
        # ----------------------------------------------------
        #

        logger.info(
            "Generating embedding for candidate search query."
        )

        embedding_model = get_embedding_model()

        query_embedding = embedding_model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

        #
        # ----------------------------------------------------
        # Retrieve relevant chunks from entire session
        # ----------------------------------------------------
        #

        logger.info(
            "Retrieving relevant resume chunks."
        )

        chunks = resume_chunks_repo.derive_resume_chunks_dynamic_similarity_threshold(
            session_id=session_id,
            query_embedding=query_embedding
        )

        if chunks is None:

            logger.error(
                "Failed retrieving resume chunks."
            )

            raise HTTPException(
                status_code=500,
                detail="Failed retrieving candidate data."
            )

        if not chunks:

            logger.info("No chunks retrived, so none satisfies the asked condition")

            return {
                "type": "chat",
                "message": "No matching candidates were found."
            }
        
        logger.info(
            "Logging {} retrieved chunk(s).",
            len(chunks),
        )

        log_retrieval_results(
            workflow="candidate_search",
            session_id=session_id,
            query=query,
            retrieved_chunks=chunks
        )

        #
        # ----------------------------------------------------
        # Group chunks by resume
        # ----------------------------------------------------
        #

        grouped_chunks = defaultdict(list)

        for chunk in chunks:
            grouped_chunks[
                chunk["resume_id"]
            ].append(chunk)

        logger.info(
            "Found {} candidate(s) with relevant chunks.",
            len(grouped_chunks),
        )

        #
        # ----------------------------------------------------
        # Build context
        # ----------------------------------------------------
        #

        candidate_contexts = []

        for resume_id, resume_chunks in grouped_chunks.items():

            candidate_name = resume_chunks[0]["candidate_name"]

            candidate_context = "\n\n".join(
                row["chunk_text"]
                for row in resume_chunks
            )

            candidate_contexts.append(
                f"""
================================================

Resume ID: {resume_id}
Candidate Name: {candidate_name}

Relevant Resume Context:

{candidate_context}

================================================
"""
            )

        if not candidate_contexts:

            return {
                "type": "chat",
                "message": "No matching candidates were found."
            }

        combined_context = "\n\n".join(candidate_contexts)

        #
        # ----------------------------------------------------
        # LLM
        # ----------------------------------------------------
        #

        logger.info(
            "Generating candidate search response."
        )

        llm_start = perf_counter()

        try:

            response = candidate_search_chain.invoke(
                {
                    "query": query,
                    "context": combined_context
                }
            )

            log_llm_usage(
                operation="Candidate Search Workflow",
                response=response,
                latency_ms=(perf_counter() - llm_start) * 1000,
                session_id=session_id,
                success=True,
            )

            logger.info("llm response | context={} | {}" , combined_context ,  response)
        
        except Exception as e:

            log_llm_usage(
                operation="Candidate Search Workflow",
                response=None,
                latency_ms=(perf_counter() - llm_start) * 1000,
                session_id=session_id,
                success=False,
                error=str(e)
            )

            raise


        # ----------------------------------------------------
        # Creating output response
        # ----------------------------------------------------

        output_response = build_candidate_search_response(
            query=query,
            matches=response.matches
        )

        logger.info(
            "Succesfully built otput response"
        )

        details = {
            "type" : "candidate_search",
            "candidates" : output_response["candidates"]
        }

        #
        # ----------------------------------------------------
        # Store chat history
        # ----------------------------------------------------
        #

        history_resp = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="chat",
            user_message=query,
            assistant_message=output_response["content"],
            details=details
        )

        if history_resp is None:

            logger.error(
                "Failed saving chat history"
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to store chat history "
                    f"for session {session_id}."
                ),
            )
            

        logger.info(
            "Candidate search completed | candidates={} | latency_ms={:.2f}",
            len(grouped_chunks),
            (perf_counter() - workflow_start) * 1000,
        )

        return {
            "type": "chat",
            "message": output_response["content"],
            "details" : details
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            "Candidate search workflow failed | error={}",
            e,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed performing candidate search.",
        )