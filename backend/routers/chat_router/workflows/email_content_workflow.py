from datetime import datetime

from fastapi import HTTPException

from routers.chat_router.chains.email_content_chian import email_chain

# from services.candidate_service import get_candidate_email
from database.active_repository import (
    email_draft_repo,
    chat_hist_repo,
    resume_repo
)


async def email_content_workflow(
    question: str,
    candidate_names: list[str],
    session_id: str,
):
    # --------------------------------------------------
    # Retrieve candidate information
    # --------------------------------------------------

    candidate_name = (
        candidate_names[0]
        if candidate_names
        else None
    )

    emails = (
        resume_repo.get_candidate_email(session_id, candidate_name)
        if candidate_name
        else []
    )

    candidate_email = emails[0] if emails else ""

    # --------------------------------------------------
    # Generate email draft using the LLM
    # --------------------------------------------------

    response = email_chain.invoke(
        {
            "question": question,
            "today": datetime.now().strftime("%Y-%m-%d"),
        }
    )

    # --------------------------------------------------
    # Store email draft in the database
    # --------------------------------------------------

    draft_response = email_draft_repo.add_data_email_draft(
        session_id=session_id,
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        subject=response.subject,
        body=response.body,
        status="draft",
        original_prompt=question,
        meeting_metadata=response.meeting_details.model_dump(),
    )

    # Raise error if draft_response is empty
    if (
        draft_response is None
    ):
        raise HTTPException(
            status_code=500,
            detail="Failed to create email draft.",
        )

    draft_id = draft_response['id']

    # --------------------------------------------------
    # Store email interaction in chat history
    # --------------------------------------------------

    chat_history_response = chat_hist_repo.add_chat_history(
        session_id=session_id,
        message_type="email",
        user_message=question,
        email_id=candidate_email,
        email_subject=response.subject,
        email_body=response.body,
        draft_id=draft_id,
        email_meeting_metadata=response.meeting_details.model_dump(),
    )

    if chat_history_response is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to store chat history for email draft.",
        )

    print("Email draft created successfully.")

    # --------------------------------------------------
    # Return email draft to the frontend
    # --------------------------------------------------

    return {
        "draft_id": draft_id,
        "type": "email",

        "email_id": candidate_email,
        "subject": response.subject,

        "body": response.body,
        "meeting_metadata": response.meeting_details.model_dump(),
        
        "actions": [
            "regenerate",
            "add_details",
            "send",
        ],
    }