from logs.log_context import get_logger
from time import perf_counter
from datetime import datetime

from fastapi import HTTPException

from routers.chat_router.chains.email_content_chian import email_chain

from database.active_repository import (
    email_draft_repo,
    chat_hist_repo,
    resume_repo,
)

from logs.llm_usage import log_llm_usage

from uuid import uuid4


async def email_content_workflow(
    question: str,
    candidate_names: list[str],
    session_id: str,
):
    
    logger = get_logger()

    workflow_start = perf_counter()

    logger.info(
        "Starting email content workflow | candidate_count=%d",
        len(candidate_names),
    )

    try:

        # --------------------------------------------------
        # Retrieve candidate information
        # --------------------------------------------------

        if len(candidate_names) == 0:

            logger.warning(
                "No candidate names found | Returning error chat message"
            )
            return {
                "type": "chat",
                "message" : "Please mention candidate name along with message"
            }


        logger.info(
            "Fetching candidate emails"
        )

        emails = (
            resume_repo.get_candidate_emails(session_id, candidate_names[0])
        )

        if emails is None:
            logger.error(
                "Failed to fetch candidate emails"
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch candidate emails.",
            )

        if len(emails) == 0 :

            logger.warning("No candidate email found for candidate = {}" , candidate_names[0])
            return{
                "type" : "chat",
                "answer" : "No such candidate found"
            }
        

        # --------------------------------------------------
        # Generate email draft
        # --------------------------------------------------

        logger.info(
            "Generating email draft"
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
            "Saving email draft"
        )

        draft_id = str(uuid4())

        draft_response = email_draft_repo.add_data_email_draft(
            draft_id = draft_id,
            session_id=session_id,
            original_prompt=question,
            candidate_name=candidate_names[0]
        )

        if draft_response is None:

            logger.error(
                "Failed to save email draft"
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to save email draft.",
            )

        # --------------------------------------------------
        # Store chat history
        # --------------------------------------------------

        logger.info(
            "Saving chat history"
        )

        chat_history_response = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="email",
            user_message=question,
            name=candidate_names[0],
            email_ids=emails,
            email_subject=response.subject,
            email_body=response.body,
            draft_id=draft_id,
            email_meeting_metadata=response.meeting_details.model_dump(),
            selected_email=emails[0]
        )

        if chat_history_response is None:

            logger.error(
                "Failed to save chat history"
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to store chat history for email draft.",
            )

        logger.info(
            "Email content workflow completed | draft_id=%s | duration=%.2fs",
            draft_id,
            perf_counter() - workflow_start,
        )

        # --------------------------------------------------
        # Return response
        # --------------------------------------------------

        return {
            "draft_id": draft_id,
            "type": "email",
            "email_ids": emails,
            "selected_email" : emails[0],
            "subject": response.subject,
            "body": response.body,
            "meeting_metadata": response.meeting_details.model_dump(),
            "actions": [
                "regenerate",
                "add_details",
                "send",
            ],
        }

    except Exception as e:

        logger.exception(
            "Unexpected error in email content workflow | {}",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate email draft",
        )