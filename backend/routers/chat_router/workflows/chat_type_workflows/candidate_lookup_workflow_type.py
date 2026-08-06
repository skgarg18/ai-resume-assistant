from datetime import datetime
from time import perf_counter
from fastapi import HTTPException

from database.active_repository import (
    resume_repo, 
    resume_chunks_repo,
    chat_hist_repo
)

from utils.log_utils import get_logger
from utils.llm_usage_log_utils import log_llm_usage
from utils.log_chunk_retrival_utils import log_retrieval_results

from services.embedding_model import encode_query

from langchain_chains.chat_workflow_chains.candidate_lookup_workflow_chain import (
    candidate_lookup_workflow_chat_chain
)


def build_candidate_lookup_response(
    candidate_payloads: list[dict],
    llm_responses: list,
    missing_names: list[str] = None,
) -> dict:
    """
    Build structured candidate lookup response.
    Returns a pure list of string bullet points in details["candidates"].
    """
    formatted_blocks = []
    candidates = []

    for payload, response in zip(candidate_payloads, llm_responses):
        name = payload["name"]
        
        # Extract list of points from Pydantic CandidateLookupResponse object
        raw_points = (
            getattr(response, "bullet_points", []) 
            if hasattr(response, "bullet_points") 
            else response.get("bullet_points", [])
        )
        
        # Clean points
        points = [pt.strip() for pt in raw_points if pt.strip()]
        
        if not points:
            points = ["The resume does not contain this information."]

        # Standard Markdown block for chat history fallback
        formatted_bullets_str = "\n".join([f"- {pt}" for pt in points])
        formatted_block = f"**{name}**\n{formatted_bullets_str}"
        formatted_blocks.append(formatted_block)

        # Pure structured object for Frontend UI
        candidates.append(
            {
                "resume_id": payload["resume_id"],
                "bullet_points": points  # <-- Returns list[str] (e.g. ["Worked at Amazon", "4 years exp"])
            }
        )

    # Separate candidates cleanly for markdown assistant message fallback
    final_message = "\n\n---\n\n".join(formatted_blocks)

    if missing_names:
        missing_str = ", ".join([f"'{m}'" for m in missing_names])
        final_message += f"\n\n*Note: No candidate record was found for {missing_str}.*"

    return {
        "content": final_message,
        "candidates": candidates
    }


async def candidate_lookup_workflow_type(
    session_id: str,
    candidate_names: list[str],
    query: str,
    original_query: str
):
    start = perf_counter()
    logger = get_logger()

    try:

        query_embedding = encode_query(query=query)

        if not candidate_names:
            logger.warning(
                "Candidate lookup requested but no candidate names were provided."
            )
            return {
                "type": "chat",
                "message": "No candidate names provided."
            }

        logger.info(
            "Candidate lookup started | candidate_count={} | candidates={}",
            len(candidate_names),
            candidate_names,
        )

        candidate_payloads = []
        missing_names = []
        seen_resume_ids = set()

        for target_name in candidate_names:
            candidates = resume_repo.get_resume_data_by_name(
                session_id=session_id,
                candidate_name=target_name,
            )

            if candidates is None:
                logger.error(
                    "Failed fetching candidate data | session_id={} | candidate={}",
                    session_id,
                    target_name,
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed fetching information for candidate '{target_name}'."
                )

            if len(candidates) == 0:
                logger.info(
                    "No candidate found in DB | candidate={}",
                    target_name,
                )
                missing_names.append(target_name)
                continue

            for candidate in candidates:
                if candidate.resume_id in seen_resume_ids:
                    continue

                seen_resume_ids.add(candidate.resume_id)

                top_chunks = resume_chunks_repo.derive_top_resume_chunks_resume_id(
                    session_id=session_id,
                    resume_id=candidate.resume_id,
                    query_embedding=query_embedding,
                    match_count=5,
                )

                if top_chunks is None:
                    logger.error(
                        "Failed retrieving chunks | candidate={}",
                        candidate.name,
                    )
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to retrieve resume chunks for {candidate.name}."
                    )

                log_retrieval_results(
                    workflow=f"candidate_lookup_{target_name}",
                    session_id=session_id,
                    query=query,
                    retrieved_chunks=top_chunks
                )

                candidate_context = "\n\n".join(
                    row["chunk_text"] for row in top_chunks
                )

                if not candidate_context:
                    continue

                candidate_payloads.append({
                    "resume_id": candidate.resume_id,
                    "name": candidate.name,
                    "context": candidate_context
                })

        if not candidate_payloads:
            logger.warning("No candidate contexts built for any requested name.")
            msg = "No matching candidates were found."
            if missing_names:
                msg = f"No candidates found matching: {', '.join(missing_names)}"
            return {
                "type": "chat",
                "message": msg
            }

        today_str = datetime.now().strftime("%d %B %Y")
        batch_inputs = [
            {
                "context": payload["context"],
                "query": query,
                "today_date": today_str
            }
            for payload in candidate_payloads
        ]

        llm_start = perf_counter()

        try:
            llm_responses = await candidate_lookup_workflow_chat_chain.abatch(batch_inputs)
            latency_ms = (perf_counter() - llm_start) * 1000

            parsed_responses = []

            for item in llm_responses:
                log_llm_usage(
                    operation="Candidate lookup Type Workflow Response",
                    response=item["raw"],
                    latency_ms=latency_ms / len(llm_responses),
                    session_id=session_id,
                    success=True
                )

                parsed_responses.append(item["parsed"])

        except Exception as e:
            log_llm_usage(
                operation="Candidate lookup Type Workflow Response",
                response=None,
                latency_ms=(perf_counter() - llm_start) * 1000,
                session_id=session_id,
                success=False,
                error=str(e),
            )
            logger.error(
                "Error during LLM invocation for candidate lookup | error={}",
                str(e)
            )
            raise

        # Build response dictionary
        final_assistant_message = build_candidate_lookup_response(
            candidate_payloads=candidate_payloads,
            llm_responses=parsed_responses,
            missing_names=missing_names,
        )

        details = {
            "type": "candidate_lookup",
            "candidates": final_assistant_message["candidates"],
            "missing_names": missing_names
        }

        # Save to Chat History
        chat_hist_response = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="chat",
            user_message=original_query,
            assistant_message=final_assistant_message["content"],
            details=details
        )

        if chat_hist_response is None:
            logger.error("Failed saving chat history")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store chat history for session {session_id}."
            )

        return {
            "type": "chat",
            "message": final_assistant_message["content"],
            "details": details
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in candidate lookup workflow | error={}", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the candidate lookup."
        )