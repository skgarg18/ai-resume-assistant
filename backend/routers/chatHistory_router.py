from fastapi import APIRouter, HTTPException
from services.supabase_client import supabase

router = APIRouter()

@router.get('/api/chat-history/{session_id}')
async def get_chat_history(session_id:str):

    try:
        response = (
            supabase.table("chat_history")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )

        return response.data or []

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )