from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


class ChatIntent(str, Enum):
    CANDIDATE_LOOKUP = "candidate_lookup"
    CANDIDATE_SEARCH = "candidate_search"
    CANDIDATE_COMPARISON = "candidate_comparison"
    CANDIDATE_RANKING = "candidate_ranking"
    GENERAL_CHAT = "general_chat"


class ChatRouterOutput(BaseModel):
    intent: ChatIntent = Field(
        description="The recruiter intent."
    )






from services.llm_initialization import llm_model
from prompts.chat_type_router_prompt import CHAT_ROUTER_PROMPT


chat_type_router_chain = (
    CHAT_ROUTER_PROMPT
    | llm_model.with_structured_output(
        ChatRouterOutput,
        method="json_mode",
        include_raw = True)
)