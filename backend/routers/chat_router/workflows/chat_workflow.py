from fastapi import HTTPException

from services.embedding_model import get_embedding_model

from database.active_repository import (
    resume_chunks_repo,
    chat_hist_repo,
)

from routers.chat_router.chains.chat_chain import chat_chain


async def chat_workflow(
    question: str,
    chat_history: list,
    matched_candidates: list[str],
    session_id: str,
):
    # --------------------------------------------------
    # Generate embedding for the user's question
    # --------------------------------------------------

    embedding_model = get_embedding_model()

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    # Stores all retrieved resume context that will be
    # passed to the LLM.
    context_parts = []

    # --------------------------------------------------
    # Retrieve relevant resume chunks
    # --------------------------------------------------

    # If one or more candidate names are detected,
    # search only within those candidates' resumes.
    if matched_candidates:

        for candidate in matched_candidates:

            results = resume_chunks_repo.derive_top_resume_chunks_similarity_search(
                session_id=session_id,
                candidate_name=candidate,
                query_embedding=query_embedding,
                match_count=5,
            )

            if results is None:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Failed to retrieve resume chunks for "
                        f"candidate {candidate} in session {session_id}."
                    ),
                )

            # Combine the retrieved chunks for this candidate.
            candidate_context = "\n\n".join(
                row["chunk_text"]
                for row in (results or [])
            )

            # Add candidate heading only if relevant context exists.
            if candidate_context:
                context_parts.append(
                    f"Candidate: {candidate}\n\n{candidate_context}"
                )

    # Otherwise, perform a semantic search across all resumes
    # in the current session.
    else:

        results = resume_chunks_repo.derive_top_resume_chunks_similarity_search(
            session_id=session_id,
            candidate_name=None,
            query_embedding=query_embedding,
            match_count=6,
        )

        if results is None:
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

    # Merge all retrieved chunks into a single context
    # that will be provided to the LLM.
    context = "\n\n".join(context_parts)

    # --------------------------------------------------
    # Generate LLM response
    # --------------------------------------------------

    final_answer = chat_chain.invoke(
        {
            "context": context,
            "question": question,
            "chat_history": chat_history,
        }
    )

    # --------------------------------------------------
    # Store chat interaction in chat history
    # --------------------------------------------------

    response = chat_hist_repo.add_chat_history(
        session_id=session_id,
        message_type="chat",
        user_message=question,
        assistant_message=final_answer,
    )

    if response is None:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to store chat history "
                f"for session {session_id}."
            ),
        )

    # --------------------------------------------------
    # Return chatbot response
    # --------------------------------------------------

    return {
        "type": "chat",
        "answer": final_answer,
    }