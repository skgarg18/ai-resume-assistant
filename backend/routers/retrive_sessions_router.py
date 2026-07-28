from utils.log_utils import get_logger
from time import perf_counter


from fastapi import APIRouter, HTTPException, Depends
from database.active_repository import session_repo

from auth.dependencies import get_current_user

router = APIRouter()

@router.get("/api/sessions")
async def get_sessions(
    current_user=Depends(get_current_user),
):
    
    logger = get_logger()

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
            "Sessions retrieved successfully | count={} | duration={:.2f}s",
            len(response),
            perf_counter() - start
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