from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from schema.email_schema import DraftRequest

from services.supabase_client import supabase

from services.email_service import send_interview_email

import traceback

router = APIRouter()


@router.post("/api/email/send")
async def send_email(
    req: DraftRequest
):

    try:

        # --------------------------------------------------
        # Fetch Draft
        # --------------------------------------------------

        result = (
            supabase.table("email_drafts")
            .select("*")
            .eq("id", req.draft_id)
            .single()
            .execute()
        )

        draft = result.data

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
                detail="Email already sent"
            )
        

        recipient_email = draft.get(
            "recipient_email"
        )

        if not recipient_email:
            raise HTTPException(
                status_code=400,
                detail="Recipient email not found"
            )

        subject = draft.get("subject")

        body = draft.get("body")

        if not subject or not body:
            raise HTTPException(
                status_code=400,
                detail="Draft is missing subject or body"
            )

        # --------------------------------------------------
        # Send Email
        # --------------------------------------------------

        print("\n========== EMAIL DEBUG ==========")
        print("Draft ID:", req.draft_id)
        print("Recipient:", recipient_email)
        print("Subject:", subject)
        print("Body Exists:", bool(body))
        print("=================================\n")

        email_result = send_interview_email(
            to_email=recipient_email,
            subject=subject,
            body=body
        )

        print("EMAIL RESULT:", email_result)

        if email_result != "Success":

            raise HTTPException(
                status_code=500,
                detail=email_result
            )

        # --------------------------------------------------
        # Update Draft Status
        # --------------------------------------------------

        now = datetime.now(
            timezone.utc
        ).isoformat()

        (
            supabase.table("email_drafts")
            .update({
                "status": "sent",
                "sent_at": now,
                "updated_at": now
            })
            .eq("id", req.draft_id)
            .execute()
        )

        # --------------------------------------------------
        # Store Chat Message
        # --------------------------------------------------

        success_message = (
            f"✓ Email sent successfully to "
            f"{recipient_email}"
        )

        (
            supabase.table("chat_history")
            .insert({
                "session_id": req.session_id,
                "message_type": "chat",
                "user_message": "Send Email",
                "assistant_message": success_message
            })
            .execute()
        )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return {
            "type": "chat",
            "answer": success_message
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n========== SEND EMAIL ERROR ==========")
        traceback.print_exc()
        print("=====================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )