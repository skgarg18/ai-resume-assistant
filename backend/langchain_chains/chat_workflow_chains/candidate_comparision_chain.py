from pydantic import BaseModel, Field


class ComparisonSection(BaseModel):
    title: str = Field(description="Section title.")
    candidate_1: str = Field(description="Information about the first candidate.")
    candidate_2: str = Field(description="Information about the second candidate.")


class ComparisonResponse(BaseModel):
    summary: str = Field(
        description="A concise 2-3 sentence summary of the comparison."
    )

    recommendation: str = Field(
        description="Overall recommendation and reasoning."
    )

    winner: str = Field(
        description="Name of the recommended candidate. Empty if no clear winner."
    )

    strengths_candidate_1: list[str]

    strengths_candidate_2: list[str]

    comparison: list[ComparisonSection]


from services.llm_initialization import llm_model
from prompts.chat_workflow_prompts.candidate_comparision_prompt import CANDIDATE_COMPARISON_PROMPT

chat_comparison_query_chain = (
    CANDIDATE_COMPARISON_PROMPT
    | llm_model.with_structured_output(
        ComparisonResponse,
        include_raw=True,
        method="json_mode"
    )
)