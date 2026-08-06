from pydantic import BaseModel, Field
from typing import List


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






# 1. Define Pydantic Schema
class QueryExpansionOutput(BaseModel):
    clean_query: str = Field(
        description="Core technical intent stripped of conversational filler, optimized for dense vector embeddings."
    )
    expanded_keywords: List[str] = Field(
        description="Comprehensive list of acronyms, full names, and related sub-skills/certifications for BM25 matching."
    )





from prompts.chat_workflow_prompts.candidate_search_prompt import (
    QUERY_EXPANDER_PROMPT
)

query_expansion_chain = (
    QUERY_EXPANDER_PROMPT
    | llm_model.with_structured_output(
        QueryExpansionOutput,
        method="json_mode",
        include_raw=True
    )
)
