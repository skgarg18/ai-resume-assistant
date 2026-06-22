from services.supabase_client import supabase


def get_candidate_email(
    session_id: str,
    candidate_name: str
) -> str | None:

    response = (
        supabase.table("resumes")
        .select("email")
        .eq("session_id", session_id)
        .ilike("name", candidate_name)
        .execute()
    )

    if response.data:
        return response.data[0]["email"]

    return None