import logging
from time import perf_counter
from datetime import datetime

logger = logging.getLogger(__name__)

from fastapi import HTTPException

from routers.chat_router.chains.email_content_chian import email_chain

from database.active_repository import (
    email_draft_repo,
    chat_hist_repo,
    resume_repo,
)

from logs.llm_usage import log_llm_usage


async def email_content_workflow(
    question: str,
    candidate_names: list[str],
    session_id: str,
):

    workflow_start = perf_counter()

    logger.info(
        "Starting email content workflow | session_id=%s | candidate_count=%d",
        session_id,
        len(candidate_names),
    )

    try:

        # --------------------------------------------------
        # Retrieve candidate information
        # --------------------------------------------------

        candidate_name = (
            candidate_names[0]
            if candidate_names
            else None
        )

        logger.info(
            "Fetching candidate email | session_id=%s | candidate=%s",
            session_id,
            candidate_name,
        )

        emails = (
            resume_repo.get_candidate_email(session_id, candidate_name)
            if candidate_name
            else []
        )

        candidate_email = emails[0] if emails else ""

        # --------------------------------------------------
        # Generate email draft
        # --------------------------------------------------

        logger.info(
            "Generating email draft | session_id=%s",
            session_id,
        )

        res_start = perf_counter()

        try:

            response = email_chain.invoke(
                {
                    "question": question,
                    "today": datetime.now().strftime("%Y-%m-%d"),
                }
            )

            log_llm_usage(
                operation="Email subject and body content generation",
                response=response["raw"],
                latency_ms=(perf_counter() - res_start)*1000,
                success=True,
                session_id=session_id
            )

        except Exception as e:
            log_llm_usage(
                operation="Email subject and body content generation",
                response=None,
                latency_ms=(perf_counter() - res_start)*1000,
                success=False,
                session_id=session_id,
                error=str(e)
            )

            raise

        response = response["parsed"]


        # --------------------------------------------------
        # Store email draft
        # --------------------------------------------------

        logger.info(
            "Saving email draft | session_id=%s",
            session_id,
        )

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

        if draft_response is None:

            logger.error(
                "Failed to save email draft | session_id=%s",
                session_id,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to create email draft.",
            )

        draft_id = draft_response["id"]

        # --------------------------------------------------
        # Store chat history
        # --------------------------------------------------

        logger.info(
            "Saving chat history | session_id=%s",
            session_id,
        )

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

            logger.error(
                "Failed to save chat history | session_id=%s",
                session_id,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to store chat history for email draft.",
            )

        logger.info(
            "Email content workflow completed | session_id=%s | draft_id=%s | duration=%.2fs",
            session_id,
            draft_id,
            perf_counter() - workflow_start,
        )

        # --------------------------------------------------
        # Return response
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

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Unexpected error in email content workflow | session_id=%s",
            session_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate email draft",
        )