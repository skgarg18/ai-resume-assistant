from fastapi import APIRouter
from schema.chat_schema import ChatRequest

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from utils.candidate_detection_util import detect_candidates

from services.embedding_model import embedding_model
from services.llm_initialization import groq_client
from services.supabase_client import supabase

from prompts.recruiter_chat_prompt import RECRUITER_CHAT_PROMPT


router = APIRouter()

@router.post("/api/{session_id}/chat")
async def chat(req: ChatRequest , session_id:str):


    matched_candidates = detect_candidates(
        req.question,
        session_id
    )

    query_embedding = embedding_model.encode(
        req.question
    ).tolist()

    context_parts = []

    if len(matched_candidates) > 0:

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
                for row in results.data
            )

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
            for row in results.data
        )
        

    context = "\n\n".join(
        context_parts
    )

    # ---------------------
    # Chat History
    # ---------------------

    chat_history = []

    for message in req.chat_history:

        if message.role == "user":

            chat_history.append(
                HumanMessage(
                    content=message.content
                )
            )

        elif message.role == "assistant":

            chat_history.append(
                AIMessage(
                    content=message.content
                )
            )


    # ---------------------
    # LangChain Prompt
    # ---------------------

    messages = RECRUITER_CHAT_PROMPT.format_messages(
        context=context,
        question=req.question,
        chat_history=chat_history
    )

    # ---------------------
    # Convert LangChain Messages
    # to Groq format
    # ---------------------



    groq_messages = []

    for msg in messages:

        role = "user"

        if msg.type == "system":
            role = "system"

        elif msg.type == "ai":
            role = "assistant"

        groq_messages.append(
            {
                "role": role,
                "content": msg.content
            }
        )


    response = groq_client.chat.completions.create(
        messages=groq_messages,
        model="llama-3.1-8b-instant"
    )

    # print("\n\n" , response)

    supabase.table("chat_history").insert({
        "session_id" : session_id,
        "user_message" : req.question,
        "assistant_message" : response.choices[0].message.content
    }).execute()


    return {
        "answer":
        response.choices[0].message.content
    }
