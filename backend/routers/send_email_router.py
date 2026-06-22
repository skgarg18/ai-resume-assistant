from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from schema.email_schema import DraftRequest

from services.supabase_client import supabase

from services.email_service import send_interview_email
from services.zoom_service import generate_zoom_link


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

        print("Starting Send operation")

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
        


        #--------------------------------------------------------
        # Add details in Email content
        # -------------------------------------------------------

        meeting_lines = []
        meeting_details = req.details


        zoom_link = ""

        if meeting_details.requires_meeting_link:

            datetime_str = (
                f"{meeting_details.date} "
                f"{meeting_details.time}"
            )

            start_dt = datetime.strptime(
                datetime_str,
                "%Y-%m-%d %H:%M"
            )


            zoom_link = generate_zoom_link(
                candidate_name=draft.get(
                    "candidate_name",
                    "Candidate"
                ),
                start_time_iso=start_dt.isoformat()
            )


            if zoom_link.endswith(
                "error-generating-link"
            ):
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate Zoom meeting"
                )

        

        if meeting_details.date:
            meeting_lines.append(
                f"- Date: {meeting_details.date}"
            )

        if meeting_details.time:
            meeting_lines.append(
                f"- Time: {meeting_details.time}"
            )

        if zoom_link:
            meeting_lines.append(
                f"- Meeting Link: {zoom_link}"
            )

        if meeting_details.comments:
            meeting_lines.append(
                f"- Notes: {meeting_details.comments}"
            )

        meeting_section = ""

        if meeting_lines:
            meeting_section = (
                "\n\nMeeting Details:\n\n"
                + "\n".join(meeting_lines)
                + "\n"
            )

        body = body.replace(
            "[[MEETING_DETAILS]]",
            meeting_section
        )

        # --------------------------------------------------
        # Send Email
        # --------------------------------------------------

        email_result = send_interview_email(
            to_email=recipient_email,
            subject=subject,
            body=body
        )


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
                "updated_at": now,
                "meeting_metadata": meeting_details.model_dump()
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


        raise HTTPException(
            status_code=500,
            detail=str(e)
        )