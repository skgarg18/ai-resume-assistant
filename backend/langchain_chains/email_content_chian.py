from pydantic import BaseModel, Field


class MeetingDetails(BaseModel):
    date: str | None = Field(
        default=None,
        description=(
            "Meeting date in YYYY-MM-DD format. "
            "Extract and normalize a clearly provided calendar date. "
            "If day and month are provided without a year, use the "
            "current year provided in the prompt. "
            "Return null if no identifiable date is provided."
        )
    )

    time: str | None = Field(
        default=None,
        description=(
            "Meeting time in 24-hour HH:MM format. "
            "Normalize explicitly provided numeric times. "
            "For example, '4pm' or '4 in the evening' becomes '16:00'. "
            "Return null if no identifiable numeric time is provided."
        )
    )

    comments: str | None = Field(
        default=None,
        description=(
            "Additional meeting instructions that are NOT already represented by "
            "date, time, or meeting platform. "
            "Examples include: 'bring your laptop', 'technical interview', "
            "'join 10 minutes early', 'camera must be on'. "
            "Do NOT include meeting platforms such as Zoom, Google Meet, "
            "Microsoft Teams, meeting links, dates, or times. "
            "Return null if there are no additional instructions."
        )
    )

    requires_meeting_link: bool = Field(
        default=False,
        description=(
            "Return true whenever the user is scheduling an interview or "
            "meeting with a candidate and does not explicitly specify that "
            "it is an in-person meeting. Also return true if the user "
            "mentions Zoom, Google Meet, Teams, online meeting, video call, "
            "virtual interview, or requests a meeting link."
        )
    )

class EmailResponse(BaseModel):
    subject: str = Field(
        description="Concise and professional email subject."
    )

    body: str = Field(
        description=(
            "Complete professional email body. May contain the exact "
            "[[MEETING_DETAILS]] placeholder for meeting-related emails."
        )
    )

    meeting_details: MeetingDetails = Field(
        default_factory=MeetingDetails,
        description=(
            "Extracted and normalized meeting or interview details "
            "from the user's request."
        )
    )


from prompts.email_content_prompt import EMAIL_PROMPT
from prompts.regenerate_email_prompt import EMAIL_REGENERATE_PROMPT

from services.llm_initialization import llm_model

email_chain = (
    EMAIL_PROMPT
    | llm_model.with_structured_output(
        EmailResponse,
        include_raw = True
    )
)


regenerate_email_chain = (
    EMAIL_REGENERATE_PROMPT
    | llm_model.with_structured_output(
        EmailResponse,
        include_raw = True
    )
)