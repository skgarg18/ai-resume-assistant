from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

from prompts.chat_workflow_prompts.candidate_lookup_type_prompt import (
    CANDIDATE_LOOKUP_TYPE_PROMPT,
)
from services.llm_initialization import llm_model


class CandidateLookupResponse(BaseModel):
    bullet_points: list[str] = Field(
        description="List of concise, factual bullet point strings directly answering the query for this candidate."
    )


# 1. Instantiate the parser
candidate_lookup_parser = PydanticOutputParser(pydantic_object=CandidateLookupResponse)

# 2. Inject format instructions into your prompt template
lookup_prompt_with_parser = CANDIDATE_LOOKUP_TYPE_PROMPT.partial(
    format_instructions=candidate_lookup_parser.get_format_instructions()
)

# 3. Step 1: Execute prompt + LLM to get the raw AIMessage
base_llm_chain = lookup_prompt_with_parser | llm_model

# 4. Step 2: Split the output into "raw" (AIMessage) and "parsed" (Pydantic model)
candidate_lookup_workflow_chat_chain = base_llm_chain | {
    "raw": RunnablePassthrough(),
    "parsed": candidate_lookup_parser,
}