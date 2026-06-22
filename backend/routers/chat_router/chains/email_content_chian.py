from pydantic import BaseModel

class EmailResponse(BaseModel):
    subject: str
    body: str

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