from utils.log_utils import bind_logger
from time import perf_counter

from fastapi import APIRouter, HTTPException, Depends
from database.active_repository import chat_hist_repo

from auth.dependencies import get_current_user

router = APIRouter()

@router.get('/api/chat-history/{session_id}')
async def get_chat_history(
    session_id:str,
    current_user=Depends(get_current_user),
    ):

    logger =  bind_logger(session_id=session_id)
    

    start = perf_counter()

    logger.info(
        "Fetching chat history"
    )

    try:

        response = chat_hist_repo.get_chat_history_by_session_id(session_id)

        if response is None:

            logger.error(
                "Failed to fetch chat history from database"
            )

            raise HTTPException(
                status_code=500,
                detail=f"Error fetching chat history from database for session {session_id}"
            )
        
        logger.info(
            "Chat history retrieved successfully| messages={} | duration={:.2f}s",
            len(response),
            perf_counter() - start,
        )

        return response or []
    
    except HTTPException:
        raise
    

    except Exception as e:

        logger.exception(
            "Unexpected error while fetching chat history"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )