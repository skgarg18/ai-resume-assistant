import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import APIRouter
from schema.chat_schema import ChatRequest

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from routers.chat_router.chains.workflow_type import workflow_router_chain

from routers.chat_router.workflows.chat_workflow import chat_workflow
from routers.chat_router.workflows.email_content_workflow import email_content_workflow

router = APIRouter()


@router.post("/api/{session_id}/chat")
async def chat(req: ChatRequest, session_id: str):

    start = perf_counter()

    logger.info(
        "Received chat request | session_id=%s",
        session_id,
    )

    try:

        # ---------------------
        # Chat History
        # ---------------------

        chat_history = [
            HumanMessage(content=m.content)
            if m.role == "user"
            else AIMessage(content=m.content)
            for m in req.chat_history
        ]

        logger.info(
            "Classifying workflow | session_id=%s",
            session_id,
        )

        workflow_response = workflow_router_chain.invoke(
            {
                "message": req.question,
                "chat_history": chat_history,
            }
        )

        logger.info(
            "Workflow classified | session_id=%s | workflow=%s",
            session_id,
            workflow_response.workflow,
        )

        if workflow_response.workflow == "chat":

            logger.info(
                "Executing chat workflow | session_id=%s",
                session_id,
            )

            response = await chat_workflow(
                req.question,
                chat_history,
                workflow_response.referenced_candidates,
                session_id,
            )

        elif workflow_response.workflow == "email":

            logger.info(
                "Executing email workflow | session_id=%s",
                session_id,
            )

            response = await email_content_workflow(
                req.question,
                workflow_response.referenced_candidates,
                session_id,
            )

        else:

            logger.error(
                "Unknown workflow returned | session_id=%s | workflow=%s",
                session_id,
                workflow_response.workflow,
            )

            response = {
                "type": "chat",
                "error": "There was an error in generating response",
            }


        logger.info(
            "Chat request completed | session_id=%s | duration=%.2fs",
            session_id,
            perf_counter() - start,
        )

        return response

    except Exception:

        logger.exception(
            "Unexpected error while processing chat request | session_id=%s",
            session_id,
        )

        return {
            "type": "chat",
            "error": "There was an error in generating response",
        }