from utils.log_utils import bind_logger
from time import perf_counter

from fastapi import APIRouter, HTTPException, Depends
from database.active_repository import resume_repo, files_repo

from auth.dependencies import get_current_user

router = APIRouter()


@router.get("/api/session/{session_id}")
async def get_session_data(
    session_id: str,
    current_user=Depends(get_current_user),
    ):

    logger = bind_logger(session_id=session_id)


    data_start = perf_counter()

    logger.info(
        "Starting extracting data for session",
    )
    try:

        results = resume_repo.get_evaluation_resume_data(session_id)

        if not results:

            logger.warning(
                "Resume Data for Session not found"
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


        formatted_results.sort(
            key=lambda x: x["overall_score"],
            reverse=True
        )

        logger.info(
            "Session data retrieved successfully | resumes=%d | duration=%.2fs",
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
            "Error fetching data for session"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )