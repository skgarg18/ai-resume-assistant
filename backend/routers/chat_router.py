from fastapi import APIRouter
from schema.chat_schema import ChatRequest

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from utils.candidate_detection_util import detect_candidates

from services.vector_db_store import chat_collection
from services.embedding_model import embedding_model
from services.llm_initialization import groq_client

from prompts.recruiter_chat_prompt import RECRUITER_CHAT_PROMPT
router = APIRouter()

@router.post("/api/chat")
async def chat(req: ChatRequest):

    matched_candidates = detect_candidates(
        req.question
    )

    query_embedding = embedding_model.encode(
        req.question
    ).tolist()

    context_parts = []

    if len(matched_candidates) > 0:

        for candidate in matched_candidates:

            results = chat_collection.query(
                query_embeddings=[query_embedding],
                where={
                    "candidate": candidate
                },
                n_results=5
            )
        
            candidate_context = "\n\n".join(
                results["documents"][0]
            )

            context_parts.append(
                f"Candidate: {candidate}\n\n{candidate_context}"
            )

    else:

        results = chat_collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

        context_parts.extend(
            results["documents"][0]
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

    return {
        "answer":
        response.choices[0].message.content
    }
