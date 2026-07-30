from utils.log_utils import get_logger
from time import perf_counter


from fastapi import HTTPException



from langchain_chains.chat_type_routers_chain import chat_type_router_chain, ChatIntent

from utils.llm_usage_log_utils import log_llm_usage

from routers.chat_router.workflows.chat_type_workflows.candidate_lookup_workflow_type import candidate_lookup_workflow_type
from routers.chat_router.workflows.chat_type_workflows.candidate_search_workflow import candidate_search_workflow
from routers.chat_router.workflows.chat_type_workflows.default_workflow_type import default_chat_workflow

async def chat_workflow(
    question: str,
    chat_history: list,
    matched_candidates: list[str],
    session_id: str,
    clean_query:str
):
    
    logger = get_logger()

    workflow_start = perf_counter()

    logger.info(
        "Starting chat workflow | matched_candidates={} | {} | clean_query={}",
        len(matched_candidates),
        matched_candidates,
        clean_query
    )

    try:

        # ---------------------------------------------------
        # Segregating type of query
        # ----------------------------------------------------

        try:
            raw_query_type = chat_type_router_chain.invoke(
                {
                    "query" : question
                }
            )

            log_llm_usage(
                operation="Chat type workflow classifier",
                response=raw_query_type["raw"],
                latency_ms=(perf_counter() - workflow_start)*1000,
                session_id=session_id,
                success=True
            )

            query_type = raw_query_type["parsed"]

            if not query_type:
                parsing_err = raw_query_type.get("parsing_error")
                raise ValueError(f"Failed to parse LLM structured output: {parsing_err}")
        
        except Exception as e:

            log_llm_usage(
                operation="Chat type workflow classifier",
                response=None,
                latency_ms=(perf_counter() - workflow_start)*1000,
                session_id=session_id,
                success=False,
                error=str(e)
            )

            raise

        
        logger.info(
            "Classified chat query into respective type | type={}",
            query_type.intent.value
        )

        
        if query_type.intent == ChatIntent.CANDIDATE_LOOKUP:
            response = await candidate_lookup_workflow_type(
                session_id=session_id,
                candidate_names=matched_candidates,
                query=clean_query,
                original_query=question
            )
            if response is None:
                logger.error(
                    "Error fetching chat response - candidate lookup"
                )

                return{
                    "type" : "chat",
                    "message" : "An unexpected error occured"
                }
            
            return response
        

        elif query_type.intent == ChatIntent.CANDIDATE_SEARCH:
            response = await candidate_search_workflow(
                session_id=session_id,
                query=clean_query,
                original_query=question
            )

            if response is None:
                logger.error(
                    "Error fetching chat response - candidate search"
                )

                return{
                    "type" : "chat",
                    "message" : "An unexpected error occured"
                }
            
            return response
        

        else:

            response = await default_chat_workflow(
                session_id=session_id,
                chat_history=chat_history,
                query=question,
                matched_candidates=matched_candidates
            )

            if response is None:
                logger.error(
                    "Error fetching chat response - default"
                )

                return{
                    "type" : "chat",
                    "message" : "An unexpected error occured"
                }
            
            return response


    except Exception as e:

        logger.error(
            "Error in chat workflow | errr={}",
            e
        )

        raise
