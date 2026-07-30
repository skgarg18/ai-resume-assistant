from utils.log_utils import get_logger
from time import perf_counter

from services.embedding_model import encode_query

from fastapi import HTTPException

from utils.llm_usage_log_utils import log_llm_usage
from utils.log_chunk_retrival_utils import log_retrieval_results

from database.active_repository import(
    chat_hist_repo,
    resume_chunks_repo
)

from langchain_chains.chat_workflow_chains.default_chain import default_chat_chain

async def default_chat_workflow(
        session_id,
        chat_history,
        query,
        matched_candidates
):
    
    logger = get_logger ()
    start = perf_counter()

    try:
        # --------------------------------------------------
        # Generate embedding
        # --------------------------------------------------

        logger.info( "Generating query embedding")


        query_embedding = encode_query(query=query)

        context_parts = []

        # --------------------------------------------------
        # Retrieve resume chunks
        # --------------------------------------------------

        logger.info(
            "Retrieving relevant resume chunks"
        )

        all_chunks = []

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
                        "Failed retrieving chunks | candidate={}",
                        candidate,
                    )

                    raise HTTPException(
                        status_code=500,
                        detail=(
                            f"Failed to retrieve resume chunks for "
                            f"candidate {candidate} in session {session_id}."
                        ),
                    )
                
                all_chunks.extend(results)

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
                    "Failed retrieving session chunks"
                )

                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Failed to retrieve resume chunks "
                        f"for session {session_id}."
                    ),
                )
            
            all_chunks.extend(results)


            context_parts.extend(
                row["chunk_text"]
                for row in (results or [])
            )


        logger.info(
            "Logging {} retrieved chunk(s).",
            len(all_chunks),
        )

        log_retrieval_results(
            workflow="default_flow",
            session_id=session_id,
            query=query,
            retrieved_chunks=all_chunks
        )

        context = "\n\n".join(context_parts)

        # --------------------------------------------------
        # LLM
        # --------------------------------------------------

        logger.info(
            "Generating LLM response"
        )

        chat_start = perf_counter()

        try:

            final_answer = default_chat_chain.invoke(
                {
                    "context": context,
                    "question": query,
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
                    operation="Chat Workflow Response",
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
            "Saving chat history"
        )

        response = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="chat",
            user_message=query,
            assistant_message=final_answer,
        )

        if response is None:

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
            "Chat workflow completed | duration={:.2f}s",
            (perf_counter() - start),
        )

        return {
            "type": "chat",
            "message": final_answer,
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Unexpected error in chat workflow"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate chat response",
        )