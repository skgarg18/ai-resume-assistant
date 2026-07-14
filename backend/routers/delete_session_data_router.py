from fastapi import APIRouter, HTTPException

from services.supabase_client import supabase, bucket_name


router = APIRouter()


@router.delete("/api/sessions/delete/{session_id}")
def delete_session(session_id: str):

    try:
        bucket = supabase.storage.from_(bucket_name)

        # -------------------------------------------------
        # 1. Check whether the session exists
        # -------------------------------------------------

        session_result = (
            supabase
            .table("sessions")
            .select("session_id")
            .eq("session_id", session_id)
            .maybe_single()
            .execute()
        )

        if not session_result.data:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )


        # -------------------------------------------------
        # 2. Fetch all files inside the session folder
        # -------------------------------------------------

        files = bucket.list(session_id)

        file_paths = [
            f"{session_id}/{file['name']}"
            for file in files
            if file.get("name")
        ]


        # -------------------------------------------------
        # 3. Delete all resume files in a single call
        # -------------------------------------------------

        if file_paths:
            bucket.remove(file_paths)


        # -------------------------------------------------
        # 4. Delete session from database
        #
        # ON DELETE CASCADE automatically deletes:
        # - resumes
        # - resume_chunks
        # - chat_history
        # - email_drafts
        # -------------------------------------------------

        (
            supabase
            .table("sessions")
            .delete()
            .eq("session_id", session_id)
            .execute()
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