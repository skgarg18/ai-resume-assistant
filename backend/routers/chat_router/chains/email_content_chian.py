from pydantic import BaseModel, Field


class MeetingDetails(BaseModel):
    date: str | None = None
    time: str | None = None
    comments: str | None = None

    # True if the user explicitly requested
    # a meeting link, Zoom meeting, online interview,
    # Google Meet, Teams, virtual meeting, etc.
    requires_meeting_link: bool = False


class EmailResponse(BaseModel):
    subject: str
    body: str
    meeting_details: MeetingDetails = Field(
        default_factory=MeetingDetails
    )

from prompts.email_content_prompt import EMAIL_PROMPT
from prompts.regenerate_email_prompt import EMAIL_REGENERATE_PROMPT

from services.llm_initialization import llm_model

email_chain = (
    EMAIL_PROMPT
    | llm_model.with_structured_output(
        EmailResponse
    )
)


regenerate_email_chain = (
    EMAIL_REGENERATE_PROMPT
    | llm_model.with_structured_output(
        EmailResponse
    )
)