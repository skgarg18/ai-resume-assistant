from utils.log_utils import bind_logger
from time import perf_counter

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

from schema.email_schema import SendEmailRequest

from database.active_repository import (
    email_draft_repo, 
    chat_hist_repo
)
from services.email_service import send_email
from services.zoom_service import generate_zoom_link

from auth.dependencies import get_current_user


router = APIRouter()

def format_time(time_str: str) -> str:
    time_obj = datetime.strptime(
        time_str,
        "%H:%M"
    )

    return time_obj.strftime("%I:%M %p")


@router.post("/api/email/send")
async def send_requested_email(
    req: SendEmailRequest,
    current_user=Depends(get_current_user),
):
    
    logger = bind_logger(
        session_id=req.session_id,
        draft_id=req.draft_id
    )

    start = perf_counter()

    logger.info("Starting email send")

    try:

        # --------------------------------------------------
        # Extract Candidate Info
        # --------------------------------------------------

        selected_candidate = req.selected_candidate or {}
        recipient_email = selected_candidate.get("email")
        candidate_name = selected_candidate.get("name", "Candidate")

        if not recipient_email:
            logger.error("Missing recipient email in selected_candidate")
            raise HTTPException(
                status_code=400,
                detail="Recipient email is required in selected_candidate."
            )

        # --------------------------------------------------
        # Fetch Draft
        # --------------------------------------------------

        logger.info("Fetching email draft")

        draft = email_draft_repo.get_data_by_draft_id(req.draft_id)

        if not draft:
            logger.error("Email draft not found")
            raise HTTPException(
                status_code=404,
                detail="Draft not found"
            )

        # --------------------------------------------------
        # Validate Draft
        # --------------------------------------------------

        if draft.get("status") == "sent":
            logger.warning("Email already sent")
            return {
                "type": "chat",
                "message": f"Email to {recipient_email} is already sent"
            }

        subject = req.subject
        body = req.body

        if not subject or not body:
            logger.warning("Draft missing subject or body")
            raise HTTPException(
                status_code=400,
                detail="Draft is missing subject or body"
            )

        # --------------------------------------------------
        # Replace Name Placeholder
        # --------------------------------------------------

        body = body.replace("[[name]]", candidate_name)

        # --------------------------------------------------
        # Add Details & Zoom in Email Content
        # --------------------------------------------------

        meeting_lines = []
        meeting_details = req.details
        zoom_link = ""

        if meeting_details.requires_meeting_link:

            logger.info("Generating Zoom meeting")

            datetime_str = (
                f"{meeting_details.date} "
                f"{meeting_details.time}"
            )

            start_dt = datetime.strptime(
                datetime_str,
                "%Y-%m-%d %H:%M"
            )

            zoom_link = generate_zoom_link(
                candidate_name=candidate_name,
                start_time_iso=start_dt.isoformat()
            )

            if zoom_link.endswith("error-generating-link"):
                logger.error("Zoom meeting generation failed")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate Zoom meeting"
                )

        if meeting_details.date:
            meeting_lines.append(f"- Date: {meeting_details.date}")

        if meeting_details.time:
            meeting_lines.append(f"- Time: {format_time(meeting_details.time)}")

        if zoom_link:
            meeting_lines.append(f"- Meeting Link: {zoom_link}")

        if meeting_details.comments:
            meeting_lines.append(f"- Notes: {meeting_details.comments}")

        meeting_section = ""

        if meeting_lines:
            meeting_section = (
                "\n\nMeeting Details:\n\n"
                + "\n".join(meeting_lines)
                + "\n"
            )

        body = body.replace("[[MEETING_DETAILS]]", meeting_section)

        # --------------------------------------------------
        # Send Email
        # --------------------------------------------------

        logger.info(
            "Sending email | recipient=%s | candidate_name=%s",
            recipient_email,
            candidate_name,
        )
        
        email_result = send_email(
            to_email=recipient_email,
            subject=subject,
            body=body,
            cc_emails=req.cc_emails,
            bcc_emails=req.bcc_emails
        )

        if email_result != "Success":

            logger.warning(
                "Email sending failed | recipient=%s | reason=%s",
                recipient_email,
                email_result,
            )

            return {
                "type": "chat",
                "message": email_result
            }

        # --------------------------------------------------
        # Update Draft Status
        # --------------------------------------------------

        logger.info("Updating draft status to sent")
        
        now = datetime.now(timezone.utc).isoformat()

        response = email_draft_repo.update_sent_email_draft(
            sent_at=now,
            updated_at=now,
            draft_id=req.draft_id,
            name=candidate_name,
            candidate_email=recipient_email
        )

        if response is None:
            logger.error("Failed to update sent status")
            raise HTTPException(
                status_code=500,
                detail="Error in updating the sent status of email draft"
            )

        # --------------------------------------------------
        # Store Chat Message
        # --------------------------------------------------

        logger.info("Saving chat history")
        
        success_message = (
            f"✓ Email sent successfully to "
            f"{candidate_name} ({recipient_email})"
        )

        response = chat_hist_repo.add_chat_history(
            session_id=req.session_id,
            message_type="chat",
            user_message="Send Email",
            assistant_message=success_message
        )

        if response is None:
            logger.error("Failed to save chat history")
            raise HTTPException(
                status_code=500,
                detail="Error in adding chat history after sending email"
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        logger.info(
            "Email sent successfully | recipient=%s | duration=%.2fs",
            recipient_email,
            perf_counter() - start,
        )
        
        return {
            "type": "chat",
            "message": success_message
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Unexpected error while sending email")

        return {
            "type": "chat",
            "message": (
                "Failed: Unable to send email. "
                "Please try again later."
            )
        }