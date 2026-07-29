from services.llm_initialization import llm_model
from prompts.chat_workflow_prompts.default_type_prompt import DEFAULT_CHAT_PROMPT

default_chat_chain = (
    DEFAULT_CHAT_PROMPT
    | llm_model
)