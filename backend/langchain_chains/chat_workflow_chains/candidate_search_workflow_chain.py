from pydantic import BaseModel, Field


class CandidateSearchMatch(BaseModel):

    resume_id: str

    candidate_name: str = Field(
        description="Candidate name."
    )

    match_reason: str = Field(
        description="A concise 1-sentence statement explaining how/why the candidate matches (e.g. explicit certification vs. hands-on technology skill)."
    )


class CandidateSearchResponse(BaseModel):

    matches: list[CandidateSearchMatch] = Field(
        description="Candidates satisfying the recruiter query."
    )




from services.llm_initialization import llm_model

from prompts.chat_workflow_prompts.candidate_search_prompt import (
    CANDIDATE_SEARCH_PROMPT,
)

candidate_search_chain = (
    CANDIDATE_SEARCH_PROMPT
    | llm_model.with_structured_output(
        CandidateSearchResponse,
        method="json_mode",
        include_raw=True
    )
)