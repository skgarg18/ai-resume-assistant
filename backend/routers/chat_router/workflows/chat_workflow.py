
from services.embedding_model import embedding_model
from services.supabase_client import supabase

from routers.chat_router.chains.chat_chain import chat_chain



async def chat_workflow( question:str , chat_history:list , matched_candidates:list[str] , session_id:str):



    query_embedding = embedding_model.encode(
        question
    ).tolist()


    context_parts = []

    if matched_candidates:

        for candidate in matched_candidates:
            results = supabase.rpc(
                "match_resume_chunks",
                {
                    "p_session_id": session_id,
                    "p_candidate_name": candidate,
                    "query_embedding": query_embedding,
                    "match_count": 5
                }
            ).execute()

            
        
            candidate_context = "\n\n".join(
                row["chunk_text"]
                for row in (results.data or [])
            )

            if candidate_context:
                context_parts.append(
                    f"Candidate: {candidate}\n\n{candidate_context}"
                )

    else:

        results = supabase.rpc(
            "match_resume_chunks",
            {
                "p_session_id": session_id,
                "p_candidate_name": None,
                "query_embedding": query_embedding,
                "match_count": 5
            }
        ).execute()

        context_parts.extend(
            row["chunk_text"]
            for row in (results.data or [])
        )
        

    context = "\n\n".join(
        context_parts
    )



    # ------------------------------------------------------------------------------------------------
    # LLM Response
    # ------------------------------------------------------------------------------------------------

    final_answer = chat_chain.invoke({
    "context": context,
    "question": question,
    "chat_history": chat_history,
    })


    supabase.table("chat_history").insert({
        "session_id" : session_id,
        "message_type": "chat",
        "user_message" : question,
        "assistant_message" : final_answer
    }).execute()


    return {
        "type" : "chat",
        "answer":final_answer
    }
