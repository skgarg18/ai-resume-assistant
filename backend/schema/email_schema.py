# schema/email_schema.py

from pydantic import BaseModel

class DraftRequest(BaseModel):
    draft_id: int
    session_id: str