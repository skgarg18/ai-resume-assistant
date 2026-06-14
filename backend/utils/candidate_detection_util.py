import re

from services.supabase_client import supabase


def detect_candidates(
    question: str,
    session_id: str
):
    response = (
        supabase.table("resumes")
        .select("name")
        .eq("session_id", session_id)
        .execute()
    )

    matched_candidates = []

    question = question.lower()

    for row in response.data:

        full_name = row["name"]

        if not full_name:
            continue

        pattern = r"\b" + re.escape(full_name.lower()) + r"\b"

        if re.search(pattern, question):
            matched_candidates.append(full_name)

    return matched_candidates