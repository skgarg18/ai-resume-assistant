import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import HTTPException

from services.embedding_model import get_embedding_model

from database.active_repository import (
    resume_chunks_repo,
    chat_hist_repo,
)

from routers.chat_router.chains.chat_chain import chat_chain

from logs.llm_usage import log_llm_usage


async def chat_workflow(
    question: str,
    chat_history: list,
    matched_candidates: list[str],
    session_id: str,
):

    workflow_start = perf_counter()

    logger.info(
        "Starting chat workflow | session_id=%s | matched_candidates=%d",
        session_id,
        len(matched_candidates),
    )

    try:

        # --------------------------------------------------
        # Generate embedding
        # --------------------------------------------------

        logger.info(
            "Generating query embedding | session_id=%s",
            session_id,
        )

        embedding_model = get_embedding_model()

        query_embedding = embedding_model.encode(
            question
        ).tolist()

        context_parts = []

        # --------------------------------------------------
        # Retrieve resume chunks
        # --------------------------------------------------

        logger.info(
            "Retrieving relevant resume chunks | session_id=%s",
            session_id,
        )

        if matched_candidates:

            for candidate in matched_candidates:

                results = resume_chunks_repo.derive_top_resume_chunks_similarity_search(
                    session_id=session_id,
                    candidate_name=candidate,
                    query_embedding=query_embedding,
                    match_count=5,
                )

                if results is None:

                    logger.error(
                        "Failed retrieving chunks | session_id=%s | candidate=%s",
                        session_id,
                        candidate,
                    )

                    raise HTTPException(
                        status_code=500,
                        detail=(
                            f"Failed to retrieve resume chunks for "
                            f"candidate {candidate} in session {session_id}."
                        ),
                    )

                candidate_context = "\n\n".join(
                    row["chunk_text"]
                    for row in (results or [])
                )

                if candidate_context:
                    context_parts.append(
                        f"Candidate: {candidate}\n\n{candidate_context}"
                    )

        else:

            results = resume_chunks_repo.derive_top_resume_chunks_similarity_search(
                session_id=session_id,
                candidate_name=None,
                query_embedding=query_embedding,
                match_count=6,
            )

            if results is None:

                logger.error(
                    "Failed retrieving session chunks | session_id=%s",
                    session_id,
                )

                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Failed to retrieve resume chunks "
                        f"for session {session_id}."
                    ),
                )

            context_parts.extend(
                row["chunk_text"]
                for row in (results or [])
            )

        context = "\n\n".join(context_parts)

        # --------------------------------------------------
        # LLM
        # --------------------------------------------------

        logger.info(
            "Generating LLM response | session_id=%s",
            session_id,
        )

        chat_start = perf_counter()

        try:

            final_answer = chat_chain.invoke(
                {
                    "context": context,
                    "question": question,
                    "chat_history": chat_history,
                }
            )

            log_llm_usage(
                operation="Chat Workflow Response",
                response=final_answer,
                latency_ms=(perf_counter() - chat_start)*1000,
                session_id=session_id,
                success=True
            )
        
        except Exception as e:
                log_llm_usage(
                    operation="Chat Workfloe Response",
                    response=None,
                    latency_ms=(perf_counter() - chat_start) * 1000,
                    session_id=session_id,
                    success=False,
                    error=str(e),
                )
                raise
        
        final_answer = final_answer.content

        # --------------------------------------------------
        # Store chat history
        # --------------------------------------------------

        logger.info(
            "Saving chat history | session_id=%s",
            session_id,
        )

        response = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="chat",
            user_message=question,
            assistant_message=final_answer,
        )

        if response is None:

            logger.error(
                "Failed saving chat history | session_id=%s",
                session_id,
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to store chat history "
                    f"for session {session_id}."
                ),
            )

        logger.info(
            "Chat workflow completed | session_id=%s | duration=%.2fs",
            session_id,
            perf_counter() - workflow_start,
        )

        return {
            "type": "chat",
            "answer": final_answer,
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Unexpected error in chat workflow | session_id=%s",
            session_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate chat response",
        )