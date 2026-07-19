
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from schema.email_schema import DraftRequest

from database.active_repository import email_draft_repo, chat_hist_repo

from routers.chat_router.chains.email_content_chian import (
    regenerate_email_chain
)


router = APIRouter()


@router.post("/api/email/regenerate")
async def regenerate_email(
    req: DraftRequest
):

    try:

        # --------------------------------------------------
        # Fetch Draft
        # --------------------------------------------------


        email_draft_response = email_draft_repo.get_data_by_draft_id(req.draft_id)

        if email_draft_response is None:
            raise HTTPException(
                status_code=404,
                detail="Error fetching draft from database"
            )

        draft = email_draft_response

        if not draft:
            raise HTTPException(
                status_code=404,
                detail="Draft not found"
            )

        # --------------------------------------------------
        # Validate Draft
        # --------------------------------------------------

        if draft.get("status") == "sent":
            raise HTTPException(
                status_code=400,
                detail="Cannot regenerate a sent email"
            )

        if not draft.get("original_prompt"):
            raise HTTPException(
                status_code=400,
                detail="Original prompt not found"
            )

        if not draft.get("subject"):
            raise HTTPException(
                status_code=400,
                detail="Previous subject not found"
            )

        if not draft.get("body"):
            raise HTTPException(
                status_code=400,
                detail="Previous email body not found"
            )

        # --------------------------------------------------
        # Generate New Draft
        # --------------------------------------------------

        response = regenerate_email_chain.invoke({
            "question": draft["original_prompt"],
            "previous_subject": draft["subject"],
            "previous_body": draft["body"],
            "details" : req.details.model_dump()
        })

        if not response:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate email"
            )

        now = datetime.now(
            timezone.utc
        ).isoformat()

        new_subject = response.subject
        new_body = response.body

        # --------------------------------------------------
        # Update Draft Table
        # --------------------------------------------------


        response = email_draft_repo.update_regenerate_email_draft_by_id(
            draft_id=req.draft_id,
            subject=new_subject,
            body=new_body,
            regeneration_count=(draft.get("regeneration_count") or 0) + 1,
            updated_at=now,
            meeting_metadata=req.details.model_dump()
        )

        if response is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to update email draft"
            )

        # --------------------------------------------------
        # Update Chat History
        # --------------------------------------------------


        response = chat_hist_repo.add_chat_history(
            session_id=req.session_id,
            user_message="Regenerate",
            draft_id=req.draft_id,
            email_subject=new_subject,
            email_body=new_body,
            email_id=draft['recipient_email'],
            message_type="email",
            email_meeting_metadata=req.details.model_dump()
        )

        if response is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to store chat history for regenerated email draft"
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return {
            "type": "email",

            "draft_id": req.draft_id,
            "email_id": draft["recipient_email"],
            "subject": new_subject,
            "body": new_body,

            "meeting_metadata" : req.details.model_dump(),

            "actions": [
                "regenerate",
                "add_details",
                "send"
            ]
        }

    except Exception as e:

        print(
            f"Regenerate Email Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to regenerate email"
        )