from utils.log_utils import bind_logger
from time import perf_counter

from fastapi import APIRouter, Depends
from schema.chat_schema import ChatRequest

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from auth.dependencies import get_current_user

from langchain_chains.workflow_type import workflow_router_chain

from routers.chat_router.workflows.chat_workflow import chat_workflow
from routers.chat_router.workflows.email_content_workflow import email_content_workflow

from utils.llm_usage_log_utils import log_llm_usage

router = APIRouter()


@router.post("/api/{session_id}/chat")
async def chat(
    req: ChatRequest,
    session_id: str,
    current_user=Depends(get_current_user)
    ):

    logger = bind_logger(session_id=session_id)
    

    start = perf_counter()

    logger.info(
        "Received chat request",

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
            "Classifying workflow"
        )

        llm_start = perf_counter()

        try:

            workflow_response = workflow_router_chain.invoke(
                {
                    "message": req.question,
                    "chat_history": chat_history,
                }
            )

            log_llm_usage(
                operation="Chat_assistant_workflow_classify",
                response=workflow_response["raw"],
                latency_ms=(perf_counter() - llm_start)*1000,
                session_id=session_id,
                success=True
            )

            workflow_response = workflow_response["parsed"]
            if not workflow_response:
                parsing_err = workflow_response.get("parsing_error")
                raise ValueError(f"Failed to parse LLM structured output: {parsing_err}")
        
        except Exception as e:

            logger.error(
                "Error in workflow classify llm call"
            )

            log_llm_usage(
                operation="Chat_assistant_workflow_classify",
                response=None,
                latency_ms=(perf_counter() - llm_start)*1000,
                session_id=session_id,
                success=False,
                error=e
            )

            raise
        

        logger.info(
            "Workflow classified | workflow={} | clean_query={}",
            workflow_response.workflow,
            workflow_response.clean_query
        )

        if workflow_response.workflow == "chat":

            logger.info("Executing chat workflow")

            response = await chat_workflow(
                req.question,
                chat_history,
                workflow_response.referenced_candidates,
                session_id,
                workflow_response.clean_query
            )

        elif workflow_response.workflow == "email":

            logger.info("Executing email workflow")

            response = await email_content_workflow(
                req.question,
                workflow_response.referenced_candidates,
                session_id,
            )

        else:

            logger.error(
                "Unknown workflow returned | workflow={}",
                workflow_response.workflow,
            )

            response = {
                "type": "chat",
                "message": "There was an error in generating response",
            }


        logger.info(
            "Chat request completed | duration={:.2f}s",
            perf_counter() - start,
        )

        return response

    except Exception:

        logger.exception(
            "Unexpected error while processing chat request"
        )

        return {
            "type": "chat",
            "message": "There was an error in generating response",
        }