from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# 1. Define Pydantic Schema for Query Expansion Output
class QueryExpansionOutput(BaseModel):
    clean_query: str = Field(
        description="Core technical intent stripped of conversational filler, optimized for dense vector embeddings."
    )
    expanded_keywords: List[str] = Field(
        description="Comprehensive list of acronyms, full names, and related sub-skills/certifications for BM25 matching."
    )


# 2. Instantiate parser to extract default format instructions
parser = JsonOutputParser(pydantic_object=QueryExpansionOutput)


# 3. Bind format_instructions via .partial()
QUERY_EXPANDER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI search query expander for a candidate resume retrieval system.

Your task is to parse conversational recruitment queries and generate optimization parameters for hybrid search (Vector + BM25):

1. `clean_query`: Strip conversational fluff (e.g., "who has", "listed in resume", "find candidates with"). Retain only core technical skills, titles, or concepts.
2. `expanded_keywords`: Generate an exhaustive list of strings for BM25 keyword matching. Include original terms, full names, common acronyms, and direct sub-services or certifications.

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON matching the exact schema below.
- Do NOT wrap response in markdown blocks (e.g., do not use ```json ... ```).
- Output the JSON payload on a single clean line without introductory or trailing text.

{format_instructions}"""),
    ("human", "Recruiter Query: {query}")
]).partial(format_instructions=parser.get_format_instructions())



CANDIDATE_SEARCH_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an AI Recruiter Assistant. Identify candidates who satisfy the recruiter's search criteria using flexible skill matching.

EVALUATION RULES:
1. Flexible/Easy Matching: Include candidates with explicit qualifications OR relevant skills, tools, technologies, or experience matching the query.
   - Example: For "Who is AWS certified?", include candidates with explicit AWS certifications AND candidates who list AWS in their tech stack or work experience.

2. Match Reason & Significance:
   - For every matched candidate, provide a concise, factual `match_reason` (1 sentence).
   - Clearly state the significance (e.g., distinguish whether they hold an explicit certification, or have hands-on experience/skills listed).

3. Independent Evaluation: Evaluate candidates individually. Do not compare or rank candidates.
4. Output Constraints: Preserve Resume ID, Candidate Name exactly as provided. If no candidates match, return an empty matches list.
CRITICAL: You MUST respond strictly in valid JSON matching the requested JSON schema.
"""
    ),
    (
        "human",
        """Recruiter Query:
{query}

Candidate Resume Context(s):
{context}"""
    )
])