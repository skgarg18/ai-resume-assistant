# services/candidate_service.py
from services.supabase_client import supabase

def get_candidate_email(session_id: str, candidate_name: str) -> str:
    """Fetch candidate email from Supabase based on name and session."""
    response = supabase.table("resumes") \
        .select("email") \
        .eq("session_id", session_id) \
        .ilike("name", f"%{candidate_name}%") \
        .execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]["email"]
    return None