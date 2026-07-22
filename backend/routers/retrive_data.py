import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException
from database.active_repository import resume_repo, files_repo

router = APIRouter()


@router.get("/api/session/{session_id}")
async def get_session_data(session_id: str):

    data_start = perf_counter()

    logger.info(
        "Starting extracting data for session | session_id=%s",
        session_id
    )
    try:

        results = resume_repo.get_resume_data_ordered_by_score(session_id)

        if not results:

            logger.warning(
                "Session not found | session_id=%s",
                session_id,
            )

            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        

        formatted_results = []

        for row in results:
            signed_url = (

                files_repo.get_signed_url(
                    row["file_url"]
                )
            )

            formatted_results.append({
                **row,
                "signed_file_url": signed_url
            })

        
        logger.info(
            "Session data retrieved successfully | session_id=%s | resumes=%d | duration=%.2fs",
            session_id,
            len(formatted_results),
            perf_counter() - data_start,
        )

        return {
            "results": formatted_results
        }
    

    except HTTPException:
        raise

    except Exception as e:
        
        logger.exception(
            "Error fetching data for session | session_id=%s",
            session_id
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )