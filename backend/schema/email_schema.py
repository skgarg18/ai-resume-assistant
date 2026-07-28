# schema/email_schema.py

from pydantic import BaseModel, Field
from langchain_chains.email_content_chian import MeetingDetails

from typing import List


class SendEmailRequest(BaseModel):
    draft_id: str
    session_id: str
    details : MeetingDetails
    subject: str
    body: str
    selected_email: str
    cc_emails: List[str] = Field(default_factory=list)
    bcc_emails: List[str] = Field(default_factory=list)


class RegenrateEmailRequest(BaseModel):
    draft_id: str
    session_id: str
    details : MeetingDetails
    subject: str
    body: str
    email_ids: List[str]
    selected_email: str
    cc_emails: List[str] = Field(default_factory=list)
    bcc_emails: List[str] = Field(default_factory=list)