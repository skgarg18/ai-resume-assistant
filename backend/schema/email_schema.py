# schema/email_schema.py

from pydantic import BaseModel, Field
from langchain_chains.email_content_chian import MeetingDetails

from typing import List, Dict, Any


class SendEmailRequest(BaseModel):
    draft_id: str
    session_id: str
    details : MeetingDetails
    subject: str
    body: str
    selected_candidate: dict
    cc_emails: List[str] = Field(default_factory=list)
    bcc_emails: List[str] = Field(default_factory=list)


class RegenrateEmailRequest(BaseModel):
    draft_id: str
    session_id: str
    details : MeetingDetails
    subject: str
    body: str
    candidates: List[Dict[str, Any]]  # Fixed typo: candiates -> candidates
    selected_candidate: Dict[str, Any]
    cc_emails: List[str] = Field(default_factory=list)
    bcc_emails: List[str] = Field(default_factory=list)