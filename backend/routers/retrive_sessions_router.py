from fastapi import APIRouter, HTTPException
from services.supabase_client import supabase

router = APIRouter()

@router.get("/api/sessions")
async def get_sessions():

    try:

        response = (
            supabase.table("sessions")
            .select("session_id, session_name, created_at")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )