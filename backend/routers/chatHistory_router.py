import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException
from database.active_repository import chat_hist_repo

router = APIRouter()

@router.get('/api/chat-history/{session_id}')
async def get_chat_history(session_id:str):

    start = perf_counter()

    logger.info(
        "Fetching chat history | session_id=%s",
        session_id,
    )

    try:

        response = chat_hist_repo.get_chat_history_by_session_id(session_id)

        if response is None:

            logger.error(
                "Failed to fetch chat history from database | session_id=%s",
                session_id,
            )

            raise HTTPException(
                status_code=500,
                detail=f"Error fetching chat history from database for session {session_id}"
            )
        
        logger.info(
            "Chat history retrieved successfully | session_id=%s | messages=%d | duration=%.2fs",
            session_id,
            len(response),
            perf_counter() - start,
        )

        return response or []
    
    except HTTPException:
        raise
    

    except Exception as e:

        logger.exception(
            "Unexpected error while fetching chat history | session_id=%s",
            session_id,
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )