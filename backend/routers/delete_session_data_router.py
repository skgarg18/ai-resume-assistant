from logs.log_context import get_logger, set_logger
from logs.logging_config import logger as base_logger
from time import perf_counter

from fastapi import APIRouter, HTTPException, Depends

from database.active_repository import session_repo, files_repo
from database.dbtype.local_storage.combined_repository import resume_chunks_repo

from auth.dependencies import get_current_user

router = APIRouter()

import traceback


@router.delete("/api/sessions/delete/{session_id}")
def delete_session(
    session_id: str,
    current_user=Depends(get_current_user),
    ):

    set_logger(
        base_logger.bind(session_id=session_id)
    )

    logger = get_logger()

    delete_start = perf_counter()

    logger.info(
        "Starting deleting data for session"
    )

    try:

        # --------------------------------------------------------
        # Delete resume chunks
        # -------------------------------------------------------

        logger.info(
            "Deleting resume chunks"
        )

        delete_chunk_response = resume_chunks_repo.delete_resume_chunks_by_session(session_id)

        if not delete_chunk_response:
            logger.error(
                "Failed to delete resume chunks"
            )

            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete chunks for {session_id}"
            )


        # -------------------------------------------------
        # 3. Delete all resume files in a single call
        # -------------------------------------------------

        logger.info(
            "Deleting uploaded resume files"
        )

        delete_file_response = files_repo.delete_session_files(session_id)   

        if not delete_file_response:

            logger.error(
                "Failed to delete session files"
            )

            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete files for {session_id}"
            )
        


        # -------------------------------------------------
        # 4. Delete session from database
        #
        # ON DELETE CASCADE automatically deletes:
        # - resumes
        # - resume_chunks
        # - chat_history
        # - email_drafts
        # -------------------------------------------------
        
        logger.info(
            "Deleting session record"
        )


        delete_session_response = session_repo.delete_session_by_id(session_id)

        if not delete_session_response:

            logger.error(
                "Failed to delete session record"
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to delete session from database"
            )
        
        logger.info(
            "Session deleted successfully | duration={:.2f}s",
            perf_counter() - delete_start,
        )


        return {
            "success": True,
            "message": "Session deleted successfully"
        }


    except HTTPException:
        raise


    except Exception as e:

        logger.exception(
            "Unexpected error while deleting session | session_id=%s",
            session_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete session"
        )