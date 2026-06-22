# schema/email_schema.py

from pydantic import BaseModel
from routers.chat_router.chains.email_content_chian import MeetingDetails



class DraftRequest(BaseModel):
    draft_id: int
    session_id: str
    details : MeetingDetails