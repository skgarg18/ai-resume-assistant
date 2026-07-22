import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from schema.email_schema import DraftRequest

from database.active_repository import email_draft_repo , chat_hist_repo

from services.email_service import send_email
from services.zoom_service import generate_zoom_link



router = APIRouter()

def format_time(time_str: str) -> str:
    time_obj = datetime.strptime(
        time_str,
        "%H:%M"
    )

    return time_obj.strftime("%I:%M %p")


@router.post("/api/email/send")
async def send_requested_email(
    req: DraftRequest
):
    
    start = perf_counter()

    logger.info(
        "Starting email send | draft_id=%s | session_id=%s",
        req.draft_id,
        req.session_id,
    )


    try:

        # --------------------------------------------------
        # Fetch Draft
        # --------------------------------------------------

        logger.info(
            "Fetching email draft | draft_id=%s",
            req.draft_id,
        )

        draft = email_draft_repo.get_data_by_draft_id(req.draft_id)

        if not draft:

            logger.error(
                "Email draft not found | draft_id=%s",
                req.draft_id,
            )
            
            raise HTTPException(
                status_code=404,
                detail="Draft not found"
            )

        # --------------------------------------------------
        # Validate Draft
        # --------------------------------------------------

        if draft.get("status") == "sent":

            logger.warning(
                "Email already sent | draft_id=%s",
                req.draft_id,
            )
            
            raise HTTPException(
                status_code=400,
                detail="Email already sent"
            )
        

        recipient_email = draft.get(
            "recipient_email"
        )

        if not recipient_email:

            logger.warning(
                "Recipient email missing | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=400,
                detail="Recipient email not found"
            )

        subject = draft.get("subject")

        body = draft.get("body")

        if not subject or not body:

            logger.warning(
                "Draft missing subject or body | draft_id=%s",
                req.draft_id,
            )
            
            raise HTTPException(
                status_code=400,
                detail="Draft is missing subject or body"
            )
        


        #--------------------------------------------------------
        # Add details in Email content
        # -------------------------------------------------------

        logger.info(
            "Generating Zoom meeting | draft_id=%s",
            req.draft_id,
        )

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
                
                logger.error(
                    "Zoom meeting generation failed | draft_id=%s",
                    req.draft_id,
                )
                
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
                f"- Time: {format_time(meeting_details.time)}"
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

        logger.info(
            "Sending email | draft_id=%s | recipient=%s",
            req.draft_id,
            recipient_email,
        )
        
        email_result = send_email(
            to_email=recipient_email,
            subject=subject,
            body=body
        )


        if email_result != "Success":

            logger.error(
                "Failed to send email | draft_id=%s | recipient=%s",
                req.draft_id,
                recipient_email,
            )
            

            raise HTTPException(
                status_code=500,
                detail=email_result
            )

        # --------------------------------------------------
        # Update Draft Status
        # --------------------------------------------------

        logger.info(
            "Updating draft status to sent | draft_id=%s",
            req.draft_id,
        )
        
        now = datetime.now(
            timezone.utc
        ).isoformat()


        response = email_draft_repo.update_sent_email_draft(
            sent_at = now,
            updated_at = now,
            meeting_metadata = meeting_details.model_dump(),
            draft_id = req.draft_id
        )

        if response is None:

            logger.error(
                "Failed to update sent status | draft_id=%s",
                req.draft_id,
            )
            
            raise HTTPException(
                status_code = 500,
                detail = "Error in updating the sent status of email draft"
            )
        

        # --------------------------------------------------
        # Store Chat Message
        # --------------------------------------------------

        logger.info(
            "Saving chat history | session_id=%s",
            req.session_id,
        )
        
        success_message = (
            f"✓ Email sent successfully to "
            f"{recipient_email}"
        )

        response = chat_hist_repo.add_chat_history(
            session_id = req.session_id,
            message_type= "chat",
            user_message= "Send Email",
            assistant_message= success_message
        )

        if response is None:

            logger.error(
                "Failed to save chat history | session_id=%s",
                req.session_id,
            )
            
            raise HTTPException(
                status_code = 500,
                detail = "Error in adding chat history after sending email"
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        logger.info(
            "Email sent successfully | draft_id=%s | recipient=%s | duration=%.2fs",
            req.draft_id,
            recipient_email,
            perf_counter() - start,
        )
        
        return {
            "type": "chat",
            "answer": success_message
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            "Unexpected error while sending email | draft_id=%s | session_id=%s",
            req.draft_id,
            req.session_id,
        )


        raise HTTPException(
            status_code=500,
            detail=str(e)
        )