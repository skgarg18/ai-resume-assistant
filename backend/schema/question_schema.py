from pydantic import BaseModel

class QuestionRequest(BaseModel):
    jd: str
    resume_text: str
