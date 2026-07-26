from logs.log_context import get_logger, set_logger
from logs.logging_config import logger as base_logger
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

    set_logger(
        base_logger.bind(session_id=session_id)
    )

    logger = get_logger()

    data_start = perf_counter()

    logger.info(
        "Starting extracting data for session",
    )
    try:

        results = resume_repo.get_resume_data(session_id)

        if not results:

            logger.warning(
                "Session not found"
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

            breakdown = row["score"]

            match_score = round(
                breakdown["technical_skills"] * 0.35
                + breakdown["professional_experience"] * 0.25
                + breakdown["project_evidence"] * 0.20
                + breakdown["education_and_training"] * 0.10
                + breakdown["domain_relevance"] * 0.10
            )

            formatted_results.append({
                **row,
                "signed_file_url": signed_url,
                "overall_score":match_score
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