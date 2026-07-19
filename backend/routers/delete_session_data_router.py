from fastapi import APIRouter, HTTPException

from database.active_repository import session_repo, files_repo
from database.dbtype.local_storage.combined_repository import resume_chunks_repo

router = APIRouter()


@router.delete("/api/sessions/delete/{session_id}")
def delete_session(session_id: str):

    try:

        # --------------------------------------------------------
        # Delete resume chunks
        # -------------------------------------------------------

        delete_chunk_response = resume_chunks_repo.delete_resume_chunks_by_session(session_id)

        if not delete_chunk_response:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete chunks for {session_id}"
            )





        # -------------------------------------------------
        # 3. Delete all resume files in a single call
        # -------------------------------------------------

        delete_file_response = files_repo.delete_session_files(session_id)   

        if not delete_file_response:
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


        delete_session_response = session_repo.delete_session_by_id(session_id)

        if not delete_session_response:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete session from database"
            )


        return {
            "success": True,
            "message": "Session deleted successfully"
        }


    except HTTPException:
        raise


    except Exception as e:

        print(
            f"Failed to delete session {session_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete session"
        )