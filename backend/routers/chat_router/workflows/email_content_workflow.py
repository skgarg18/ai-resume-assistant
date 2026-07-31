from utils.log_utils import get_logger
from time import perf_counter
from datetime import datetime

from fastapi import HTTPException

from langchain_chains.email_content_chian import email_chain

from database.active_repository import (
    email_draft_repo,
    chat_hist_repo,
    resume_repo,
)

from utils.llm_usage_log_utils import log_llm_usage

from uuid import uuid4


async def email_content_workflow(
    question: str,
    candidate_names: list[str],
    session_id: str,
    clean_query:str
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

        if not candidate_names:

            logger.warning(
                "No candidate names found | Returning error chat message"
            )
            return {
                "type": "chat",
                "message": "Please mention candidate name along with message"
            }

        logger.info("Fetching candidate resume details")

        candidates = []
        seen_emails = set()

        for candidate_name in candidate_names:
            resumes = resume_repo.get_resume_data_by_name(
                session_id=session_id,
                candidate_name=candidate_name,
            )

            if resumes is None:
                logger.error("Failed to fetch candidate details for name=%s", candidate_name)
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch candidate details.",
                )

            for resume in resumes:
                if resume.email and resume.email not in seen_emails:
                    seen_emails.add(resume.email)
                    candidates.append({
                        "resume_id": getattr(resume, "id", getattr(resume, "resume_id", None)),
                        "name": resume.name,
                        "email": resume.email,
                        "match_score": getattr(resume, "match_score", None),
                    })

        if not candidates:
            logger.warning("No candidate emails found for candidate_names=%s", candidate_names)
            return {
                "type": "chat",
                "message": "No such candidate found"
            }

        # Default selected candidate is the first match
        selected_candidate = candidates[0]

        # --------------------------------------------------
        # Generate email draft
        # --------------------------------------------------

        logger.info("Generating email draft")

        res_start = perf_counter()

        try:

            response = email_chain.invoke(
                {
                    "question": clean_query,
                    "today": datetime.now().strftime("%Y-%m-%d"),
                }
            )

            log_llm_usage(
                operation="Email subject and body content generation",
                response=response["raw"],
                latency_ms=(perf_counter() - res_start) * 1000,
                success=True,
                session_id=session_id
            )

        except Exception as e:
            log_llm_usage(
                operation="Email subject and body content generation",
                response=None,
                latency_ms=(perf_counter() - res_start) * 1000,
                success=False,
                session_id=session_id,
                error=str(e)
            )

            raise

        response = response["parsed"]

        # --------------------------------------------------
        # Store email draft
        # --------------------------------------------------

        logger.info("Saving email draft")

        draft_id = str(uuid4())

        draft_response = email_draft_repo.add_data_email_draft(
            draft_id=draft_id,
            session_id=session_id,
            original_prompt=question,
            candidate_name=selected_candidate["name"]
        )

        if draft_response is None:

            logger.error("Failed to save email draft")

            raise HTTPException(
                status_code=500,
                detail="Failed to save email draft.",
            )

        # --------------------------------------------------
        # Store chat history
        # --------------------------------------------------

        logger.info("Saving chat history")

        chat_history_response = chat_hist_repo.add_chat_history(
            session_id=session_id,
            message_type="email",
            user_message=question,
            candidates=candidates,                 # Replaced old attributes with the full candidates list
            selected_candidate=selected_candidate, # Replaced selected_email with the full object
            email_subject=response.subject,
            email_body=response.body,
            draft_id=draft_id,
            email_meeting_metadata=response.meeting_details.model_dump(),
        )

        if chat_history_response is None:

            logger.error("Failed to save chat history")

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
        # Return response to UI
        # --------------------------------------------------

        return {
            "draft_id": draft_id,
            "type": "email",
            "candidates": candidates,
            "selected_candidate": selected_candidate,
            "subject": response.subject,
            "body": response.body,
            "meeting_metadata": response.meeting_details.model_dump(),
            "cc_emails": [],
            "bcc_emails": [],
            "actions": [
                "regenerate",
                "add_details",
                "send",
            ],
        }

    except Exception as e:

        logger.exception(
            "Unexpected error in email content workflow | %s",
            e
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate email draft",
        )