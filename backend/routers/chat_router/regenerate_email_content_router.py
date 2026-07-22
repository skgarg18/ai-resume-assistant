import logging
from time import perf_counter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException

from schema.email_schema import DraftRequest

from logs.llm_usage import log_llm_usage

from database.active_repository import (
    email_draft_repo,
    chat_hist_repo,
)

from routers.chat_router.chains.email_content_chian import (
    regenerate_email_chain,
)

router = APIRouter()


@router.post("/api/email/regenerate")
async def regenerate_email(
    req: DraftRequest
):

    start = perf_counter()

    logger.info(
        "Starting email regeneration | draft_id=%s | session_id=%s",
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

        email_draft_response = email_draft_repo.get_data_by_draft_id(
            req.draft_id
        )

        if email_draft_response is None:

            logger.error(
                "Failed to fetch email draft | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=404,
                detail="Error fetching draft from database",
            )

        draft = email_draft_response

        if not draft:

            logger.warning(
                "Email draft not found | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=404,
                detail="Draft not found",
            )

        # --------------------------------------------------
        # Validate Draft
        # --------------------------------------------------

        if draft.get("status") == "sent":

            logger.warning(
                "Attempted to regenerate sent email | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=400,
                detail="Cannot regenerate a sent email",
            )

        if not draft.get("original_prompt"):

            logger.warning(
                "Original prompt missing | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=400,
                detail="Original prompt not found",
            )

        if not draft.get("subject"):

            logger.warning(
                "Previous subject missing | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=400,
                detail="Previous subject not found",
            )

        if not draft.get("body"):

            logger.warning(
                "Previous body missing | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=400,
                detail="Previous email body not found",
            )

        # --------------------------------------------------
        # Generate New Draft
        # --------------------------------------------------

        logger.info(
            "Generating regenerated email | draft_id=%s",
            req.draft_id,
        )

        regen_start = perf_counter()

        try:

            response = regenerate_email_chain.invoke(
                {
                    "question": draft["original_prompt"],
                    "previous_subject": draft["subject"],
                    "previous_body": draft["body"],
                    "details": req.details.model_dump(),
                }
            )

            log_llm_usage(
                operation="Regenerating email content",
                response=response["raw"],
                latency_ms=(perf_counter() - regen_start) * 1000,
                session_id=req.session_id,
                success=True,
            )

        except Exception as e:
        
            log_llm_usage(
                operation="Regenerating email content",
                response=None,
                latency_ms=(perf_counter() - regen_start) * 1000,
                session_id=req.session_id,
                success=False,
                error=str(e),
            )

            raise

        if not response:

            logger.error(
                "Failed to generate regenerated email | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to generate email",
            )
        
        response = response["parsed"]
        

        now = datetime.now(
            timezone.utc
        ).isoformat()

        new_subject = response.subject
        new_body = response.body

        # --------------------------------------------------
        # Update Draft Table
        # --------------------------------------------------

        logger.info(
            "Updating regenerated email draft | draft_id=%s",
            req.draft_id,
        )

        response = email_draft_repo.update_regenerate_email_draft_by_id(
            draft_id=req.draft_id,
            subject=new_subject,
            body=new_body,
            regeneration_count=(
                draft.get("regeneration_count") or 0
            ) + 1,
            updated_at=now,
            meeting_metadata=req.details.model_dump(),
        )

        if response is None:

            logger.error(
                "Failed to update regenerated email draft | draft_id=%s",
                req.draft_id,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to update email draft",
            )

        # --------------------------------------------------
        # Update Chat History
        # --------------------------------------------------

        logger.info(
            "Saving regenerated email to chat history | session_id=%s",
            req.session_id,
        )

        response = chat_hist_repo.add_chat_history(
            session_id=req.session_id,
            user_message="Regenerate",
            draft_id=req.draft_id,
            email_subject=new_subject,
            email_body=new_body,
            email_id=draft["recipient_email"],
            message_type="email",
            email_meeting_metadata=req.details.model_dump(),
        )

        if response is None:

            logger.error(
                "Failed to save regenerated email chat history | session_id=%s",
                req.session_id,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to store chat history for regenerated email draft",
            )

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        logger.info(
            "Email regenerated successfully | draft_id=%s | duration=%.2fs",
            req.draft_id,
            perf_counter() - start,
        )

        return {
            "type": "email",
            "draft_id": req.draft_id,
            "email_id": draft["recipient_email"],
            "subject": new_subject,
            "body": new_body,
            "meeting_metadata": req.details.model_dump(),
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
            "Unexpected error while regenerating email | draft_id=%s | session_id=%s",
            req.draft_id,
            req.session_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to regenerate email",
        )