from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from prompts.chat_workflow_prompts.candidate_lookup_type_prompt import (
    CANDIDATE_LOOKUP_TYPE_PROMPT,
)
from services.llm_initialization import llm_model


class CandidateLookupResponse(BaseModel):
    bullet_points: list[str] = Field(
        description="List of concise, factual bullet point strings directly answering the query for this candidate."
    )


# Instantiate standard parser
candidate_lookup_parser = PydanticOutputParser(pydantic_object=CandidateLookupResponse)

# Pass parser instructions into the prompt template
lookup_prompt_with_parser = CANDIDATE_LOOKUP_TYPE_PROMPT.partial(
    format_instructions=candidate_lookup_parser.get_format_instructions()
)

# Chain parser directly without forced API tool calling
candidate_lookup_workflow_chat_chain = (
    lookup_prompt_with_parser
    | llm_model
    | candidate_lookup_parser
)