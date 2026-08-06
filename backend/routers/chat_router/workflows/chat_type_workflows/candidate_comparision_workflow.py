from fastapi import HTTPException

from time import perf_counter

from langchain_chains.chat_workflow_chains.candidate_comparision_chain import chat_comparison_query_chain, ComparisonResponse

from services.embedding_model import encode_query

from database.active_repository import(
    resume_chunks_repo,
    chat_hist_repo
)

from utils.log_utils import get_logger
from utils.llm_usage_log_utils import log_llm_usage
from utils.log_chunk_retrival_utils import log_retrieval_results



def build_response(response: ComparisonResponse) -> str:
    """
    Converts a structured comparison response into a plain-text
    representation suitable for storing in chat history.

    This text is never shown directly in the UI. It is stored so that
    future LLM calls have readable conversational context.
    """

    history = []

    history.append("Candidate Comparison")

    if response.summary:
        history.append(f"\nSummary:\n{response.summary}")

    if response.winner:
        history.append(f"\nRecommended Candidate:\n{response.winner}")

    if response.recommendation:
        history.append(
            f"\nRecommendation:\n{response.recommendation}"
        )

    if response.strengths_candidate_1:
        history.append("\nStrengths of Candidate 1:")

        for point in response.strengths_candidate_1:
            history.append(f"- {point}")

    if response.strengths_candidate_2:
        history.append("\nStrengths of Candidate 2:")

        for point in response.strengths_candidate_2:
            history.append(f"- {point}")

    if response.comparison:
        history.append("\nDetailed Comparison:")

        for section in response.comparison:
            history.append(
                f"""
{section.title}

Candidate 1:
{section.candidate_1}

Candidate 2:
{section.candidate_2}
""".strip()
            )

    return "\n".join(history)



async def candidate_comparision_workflow(
    session_id: str,
    candidate_names: list[str],
    query: str,
    original_query: str
):
    workflow_start = perf_counter()
    logger = get_logger()

    try:
        # 1. Input Validation
        if len(candidate_names) < 2:
            logger.warning(
                "Candidate comparison requested with fewer than 2 candidates | session_id={} candidates={}",
                session_id,
                candidate_names
            )
            return {
                "type": "chat",
                "message": "At least two candidates are required for comparison."
            }

        if len(candidate_names) > 2:
            logger.warning(
                "More than 2 candidates passed to pairwise comparison; utilizing first two | candidates={}",
                candidate_names
            )

        query_embedding = encode_query(query=query)
        context_parts = {}

        # 2. Retrieval Phase
        for candidate in candidate_names[:2]:
            results = resume_chunks_repo.derive_top_resume_chunks_similarity_search(
                session_id=session_id,
                candidate_name=candidate,
                query_embedding=query_embedding,
                match_count=5,
            )

            if results is None:
                logger.error(
                    "Failed retrieving chunks from repository | candidate={} session_id={}",
                    candidate,
                    session_id
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to retrieve resume chunks for candidate {candidate}."
                )

            if not results:
                logger.warning(
                    "Zero chunks retrieved for candidate | candidate={} session_id={}",
                    candidate,
                    session_id
                )

            log_retrieval_results(
                workflow="candidate_comparison",
                session_id=session_id,
                query=query,
                retrieved_chunks=results
            )

            candidate_context = "\n\n".join([chunk["chunk_text"] for chunk in results])
            context_parts[candidate] = candidate_context

        logger.info(
            "Retrieved context for candidate comparison | candidates={} session_id={}",
            candidate_names[:2],
            session_id
        )

        # 3. LLM Generation Phase
        llm_start = perf_counter()
        try:
            llm_response = chat_comparison_query_chain.invoke(
                {
                    "candidate_1": candidate_names[0],
                    "candidate_2": candidate_names[1],
                    "candidate_1_context": context_parts.get(candidate_names[0], ""),
                    "candidate_2_context": context_parts.get(candidate_names[1], ""),
                    "query": query
                }
            )
            latency_ms = (perf_counter() - llm_start) * 1000

            log_llm_usage(
                operation="Candidate comparison workflow",
                response=llm_response.get("raw"),
                latency_ms=latency_ms,
                session_id=session_id,
                success=True
            )

        except Exception as e:
            log_llm_usage(
                operation="Candidate comparison workflow",
                response=None,
                latency_ms=(perf_counter() - llm_start) * 1000,
                session_id=session_id,
                success=False,
                error=str(e)
            )
            logger.exception(
                "Error during LLM invocation for comparison | session_id={}",
                session_id
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to generate structured comparison from model response."
            )

        parsed_response = llm_response.get("parsed")
        if parsed_response is None:
            parsing_error = llm_response.get("parsing_error")
            logger.error(
                "Failed to parse LLM response into ComparisonResponse | error={} session_id={}",
                parsing_error,
                session_id
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to generate structured comparison from model response."
            )

        # 4. Storage Phase
        details = {
            "type": "candidate_comparison",
            "data": parsed_response.model_dump()
        }
        formatted_message = build_response(parsed_response)

        hist_resp = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="chat",
            user_message=original_query,
            assistant_message=formatted_message,
            details=details
        )

        if hist_resp is None:
            logger.error(
                "Failed to store chat history for comparison | session_id={}",
                session_id
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to store chat history for candidate comparison."
            )

        total_duration_ms = (perf_counter() - workflow_start) * 1000
        logger.info(
            "Candidate comparison workflow completed successfully | candidates={} session_id={} duration_ms={:.2f}",
            candidate_names[:2],
            session_id,
            total_duration_ms
        )

        return {
            "type": "chat",
            "message": formatted_message,
            "details": details
        }

    except HTTPException:
        # Re-raise explicit HTTP exceptions directly
        raise

    except Exception as e:
        logger.exception(
            "Unexpected error in candidate comparison workflow | session_id={}",
            session_id
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during candidate comparison."
        )