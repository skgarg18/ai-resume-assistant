from logs.log_context import get_logger, set_logger
from logs.logging_config import logger as base_logger
from time import perf_counter
from datetime import datetime, timezone


from fastapi import APIRouter, HTTPException, Depends

from schema.email_schema import RegenrateEmailRequest

from logs.llm_usage import log_llm_usage

from database.active_repository import (
    email_draft_repo,
    chat_hist_repo,
)

from routers.chat_router.chains.email_content_chian import (
    regenerate_email_chain,
)

from auth.dependencies import get_current_user

router = APIRouter()


@router.post("/api/email/regenerate")
async def regenerate_email(
    req: RegenrateEmailRequest,
    current_user=Depends(get_current_user),
):
    
    set_logger(
        base_logger.bind(
            session_id=req.session_id,
            draft_id=req.draft_id)
    )

    logger = get_logger()

    start = perf_counter()

    logger.info(
        "Starting email regeneration"
    )

    try:

        # --------------------------------------------------
        # Fetch Draft
        # --------------------------------------------------

        logger.info(
            "Fetching email draft"
        )

        email_draft_response = email_draft_repo.get_data_by_draft_id(
            req.draft_id
        )

        if email_draft_response is None:

            logger.error(
                "Failed to fetch email draft"
            )

            raise HTTPException(
                status_code=404,
                detail="Error fetching draft from database",
            )

        draft = email_draft_response

        if not draft:

            logger.warning(
                "Email draft not found"
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
                "Attempted to regenerate sent email"
            )

            return{
                "type" : "chat",
                "message" : "Email has been already sent to this candidate"
            }

        if not draft.get("original_prompt"):

            logger.warning(
                "Original prompt missing"
            )

            raise HTTPException(
                status_code=400,
                detail="Original prompt not found",
            )

        # --------------------------------------------------
        # Generate New Draft
        # --------------------------------------------------

        logger.info(
            "Generating regenerated email"
        )

        regen_start = perf_counter()

        try:

            response = regenerate_email_chain.invoke(
                {
                    "question": draft["original_prompt"],
                    "previous_subject": req.subject,
                    "previous_body": req.body,
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
                "Failed to generate regenerated email"
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
            "Updating regenerated email draft"
        )

        response = email_draft_repo.update_regenerate_email_draft_by_id(
            draft_id=req.draft_id,
            regeneration_count=(
                draft.get("regeneration_count") or 0
            ) + 1,
            updated_at=now,
        )

        if response is None:

            logger.error(
                "Failed to update regenerated email draft"
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to update email draft",
            )

        # --------------------------------------------------
        # Update Chat History
        # --------------------------------------------------

        logger.info(
            "Saving regenerated email to chat history"
        )

        response = chat_hist_repo.add_chat_history(
            session_id=req.session_id,
            user_message="Regenerate",
            draft_id=req.draft_id,
            email_subject=new_subject,
            email_body=new_body,
            email_ids=req.email_ids,
            selected_email=req.selected_email,
            message_type="email",
            email_meeting_metadata=req.details.model_dump(),
        )

        if response is None:

            logger.error(
                "Failed to save regenerated email chat history"
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to store chat history for regenerated email draft",
            )

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        logger.info(
            "Email regenerated successfully | duration={:.2f}s",
            perf_counter() - start,
        )

        return {
            "type": "email",
            "draft_id": req.draft_id,
            "email_ids": req.email_ids,
            "subject": new_subject,
            "body": new_body,
            "meeting_metadata": req.details.model_dump(),
            "selected_email" : req.selected_email,
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
            "Unexpected error while regenerating email"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to regenerate email",
        )