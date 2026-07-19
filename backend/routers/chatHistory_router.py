from fastapi import APIRouter, HTTPException
from database.active_repository import chat_hist_repo

router = APIRouter()

@router.get('/api/chat-history/{session_id}')
async def get_chat_history(session_id:str):

    try:
        # response = (
        #     supabase.table("chat_history")
        #     .select("*")
        #     .eq("session_id", session_id)
        #     .order("created_at")
        #     .execute()
        # )

        response = chat_hist_repo.get_chat_history_by_session_id(session_id)

        if response is None:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching chat history from database for session {session_id}"
            )

        return response or []

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )