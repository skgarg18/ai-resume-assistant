from services.llm_initialization import llm_model
from prompts.recruiter_chat_prompt import RECRUITER_CHAT_PROMPT
from langchain_core.output_parsers import StrOutputParser

chat_chain = (
    RECRUITER_CHAT_PROMPT
    | llm_model
    | StrOutputParser()
)