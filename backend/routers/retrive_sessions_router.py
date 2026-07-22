import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException
from database.active_repository import session_repo

router = APIRouter()

@router.get("/api/sessions")
async def get_sessions():

    start = perf_counter()

    logger.info(
        "Starting extraction of session"
    )

    try:



        response = session_repo.get_sessions()



        if response is None:

            logger.error(
                "Error fetching sessions data"
            )

            raise HTTPException(
                status_code=404,
                detail="Error fetching sessions"
            )

        logger.info(
            "Sessions retrieved successfully | count=%d | duration=%.2fs",
            len(response),
            perf_counter() - start,
        )

        return response
    

    except HTTPException:
        raise


    except Exception as e:

        logger.exception(
            "Unexpected error while fetching sessions"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )