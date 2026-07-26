from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

# -------------------------------------------------------------------
# Basic Info
# -------------------------------------------------------------------


class OnlineProfile(BaseModel):
    """Stores online profiles like GitHub, LinkedIn, etc. from the resume."""

    model_config = ConfigDict(extra="forbid")

    platform: str = Field(
        description="Platform name such as LinkedIn, GitHub, LeetCode, Kaggle, Codeforces, Medium, etc."
    )
    url: str = Field(
        description="Profile URL exactly as mentioned. Empty string if not found."
    )


class BasicInfo(BaseModel):
    """Basic candidate information. All string fields must always be present;
    use empty string '' when the information is not available in the resume."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="Candidate's full name exactly as mentioned in the resume. Empty string if not found."
    )
    email: str = Field(
        description="Primary email address. Empty string if not found."
    )
    phone: str = Field(
        description="Primary contact number. Empty string if not found."
    )
    location: str = Field(
        description="Current city/state/country if available. Empty string if not found."
    )
    online_profiles: List[OnlineProfile] = Field(
        description="Professional online profiles such as LinkedIn, GitHub, LeetCode, Kaggle, Medium, etc. Empty list if none found."
    )
    current_designation: str = Field(
        description="Latest/current job title. Empty string if not found."
    )
    total_experience_years: Optional[float] = Field(
        ge=0,
        description=(
            "Leave this as null. Total experience is calculated programmatically "
            "from extracted start_date/end_date values, not by the model."
        ),
    )


# --------------------------------------------------------------------
# Education Info
# ---------------------------------------------------------------------

class AcademicScore(BaseModel):
    """Academic score, numeric or descriptive (e.g. 'First Class')."""

    model_config = ConfigDict(extra="forbid")

    score: Optional[float] = Field(
        description="Numeric score if the resume gives one (e.g., CGPA or Percentage). Null if not numeric."
    )
    raw_value: Optional[str] = Field(
        description="Original score text if not numeric, e.g. 'First Class', 'Distinction'. Null if score is numeric."
    )
    type: Literal["CGPA", "Percentage", "Grade", "Other"] = Field(
        description="Type of academic score."
    )


class Education(BaseModel):
    """A single education record. String fields default to '' when unknown;
    year/score fields default to null when unknown."""

    model_config = ConfigDict(extra="forbid")

    degree: str = Field(
        description="Degree obtained. Empty string if not found."
    )
    specialization: str = Field(
        description="Major or specialization. Empty string if not found."
    )
    institution: str = Field(
        description="College, institute or university, preserved exactly. Empty string if not found."
    )
    location: str = Field(
        description="Institution's city/state/country if mentioned. Empty string if not found."
    )
    start_year: Optional[int] = Field(
        description="Year education started. Null if not mentioned."
    )
    end_year: Optional[int] = Field(
        description="Year education completed or expected to complete. Null if not mentioned."
    )
    academic_score: Optional[AcademicScore] = Field(
        description="Academic score if mentioned. Null if not mentioned."
    )


# -----------------------------------------------------------------
# Experience
# ------------------------------------------------------------------


class Experience(BaseModel):
    """A single professional experience record."""

    model_config = ConfigDict(extra="forbid")

    company: str = Field(
        description="Company name, preserved exactly."
    )
    designation: str = Field(
        description="Job title. Empty string if not found."
    )
    employment_type: str = Field(
        description="Type of employment (e.g., Full-time, Internship, Contract). Empty string if not found."
    )
    start_date: str = Field(
        description=(
            "Employment start date normalized to 'YYYY-MM' if month and year are known, "
            "or 'YYYY' if only the year is known. Empty string if not found."
        )
    )
    end_date: str = Field(
        description=(
            "Employment end date, same normalization as start_date. "
            "Empty string if not found or if currently working."
        )
    )
    location: str = Field(
        description="Employment location. Empty string if not found."
    )
    currently_working: Optional[bool] = Field(
        description="Whether this is the candidate's current job. Null if unclear."
    )
    description: List[str] = Field(
        description="Original responsibilities/work description from the resume, minor formatting cleanup only.",
    )
    technologies_used: List[str] = Field(
        description="Technologies, frameworks, tools and platforms explicitly used in this role.",
    )


# ----------------------------------------------------------------------------------
# Project
# ----------------------------------------------------------------------------------

class Project(BaseModel):
    """A single project record."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        description="Project title exactly as mentioned in the resume."
    )
    description: List[str] = Field(
        description=(
            "Original project description from the resume with only minor formatting cleanup. "
            "Do not summarize, rewrite or omit technical details."
        ),
    )
    technologies: List[str] = Field(
        description="Technologies, frameworks, libraries, tools and platforms explicitly used in the project.",
    )


# -------------------------------------------------------------------------
# Certifications
# -------------------------------------------------------------------------

class Certification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description="Certification name, preserved exactly."
    )
    issuing_organization: str = Field(
        description="Organization that issued the certification. Empty string if not found."
    )
    issue_date: str = Field(
        description=(
            "Date or year the certification was issued, preserved or normalized "
            "as mentioned in the resume (e.g., '2022', 'Aug 2022', '2022-08', or '2022-08-15'). "
            "Empty string '' if not mentioned."
        )
    )


class Achievement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(
        description=(
            "Achievement exactly as mentioned in the resume. "
            "Do not categorize or rewrite it. Preserve important details such as rankings, "
            "awards, publications, hackathons, leadership roles, scholarships, patents, "
            "or other accomplishments."
        )
    )


# ---------------------------------------------------------------------------
# Derived Specific Insights
# ---------------------------------------------------------------------------

class RecruiterInsight(BaseModel):
    """A single job-independent recruiter takeaway with supporting evidence."""

    model_config = ConfigDict(extra="forbid")

    category: Literal[
        "Company Background",
        "AI & Emerging Tech",
        "Leadership",
        "Architecture",
        "Career Progression",
        "Education",
        "Research",
        "Open Source",
        "Entrepreneurship",
        "Domain Expertise",
    ] = Field(
        description=(
            "The broad career differentiator represented by this insight. "
            "Choose the single closest-fit category from the fixed list — never invent a new one."
        )
    )
    insight: str = Field(
        description=(
            "A concise recruiter takeaway (5-12 words) describing a long-term, "
            "job-independent differentiator of the candidate. Focus on why the candidate "
            "stands out rather than what they specifically did. Do not include metrics, "
            "technologies, project names, or resume bullet points unless absolutely necessary."
        )
    )
    evidence: str = Field(
        max_length=300,
        description=(
            "A short (1-2 sentence) resume excerpt, lightly cleaned, that directly supports "
            "the insight. Do not duplicate full paragraphs already captured in Experience or "
            "Projects sections. Do not paraphrase into another summary."
        ),
    )
    importance: Literal["High", "Medium", "Low"] = Field(
        description=(
            "High = career-defining, rare signal. "
            "Medium = meaningful differentiator but not rare. "
            "Low = minor but useful observation."
        )
    )


# ----------------------------------------------------------------------------------------------
# CALL 1 SCHEMA — faithful extraction (no judgment calls)
# ----------------------------------------------------------------------------------------------
 
class ResumeMetadataPart1(BaseModel):
    """Output schema for the first LLM call: faithful transcription of resume content."""
 
    model_config = ConfigDict(extra="forbid")
 
    basic_info: BasicInfo
    education: List[Education] = Field(description="Reverse chronological")
    experience: List[Experience] = Field(description="Reverse chronological")
    projects: List[Project]
    certifications: List[Certification]
    achievements: List[Achievement] = Field(max_length=15)
    languages: List[str] = Field(description="Spoken languages")
 
 
# ----------------------------------------------------------------------------------------------
# CALL 2 SCHEMA — derived / analytical fields (needs judgment, grounded in resume text)
# ----------------------------------------------------------------------------------------------
 
class ResumeMetadataPart2(BaseModel):
    """Output schema for the second LLM call: derived recruiter-facing analysis."""
 
    model_config = ConfigDict(extra="forbid")
    
    
    resume_summary: str = Field(description="Exact summary/about text if present, else ''")
    skills: List[str] = Field( description="Only explicitly stated skills, deduped")
    recruiter_insights: List[RecruiterInsight] = Field(description="2-5 insights")
    search_tags: List[str] = Field( description="10-20 normalized search tags")
 
 
# ----------------------------------------------------------------------------------------------
# FINAL COMBINED SCHEMA — merged result of both calls (not sent to the LLM directly)
# ----------------------------------------------------------------------------------------------
 
class ResumeMetadata(BaseModel):
    """Final structured resume analysis output, merged from Part1 + Part2 LLM calls."""
 
    model_config = ConfigDict(extra="forbid")
 
    basic_info: BasicInfo
    education: List[Education]
    experience: List[Experience]
    projects: List[Project]
    skills: List[str]
    certifications: List[Certification]
    achievements: List[Achievement]
    recruiter_insights: List[RecruiterInsight]
    search_tags: List[str]
    languages: List[str]
    resume_summary: str
 
    @classmethod
    def from_parts(cls, part1: ResumeMetadataPart1, part2: ResumeMetadataPart2) -> "ResumeMetadata":
        """Merge the two partial LLM outputs into the final combined schema."""
        return cls(
            basic_info=part1.basic_info,
            education=part1.education,
            experience=part1.experience,
            projects=part1.projects,
            skills=part2.skills,
            certifications=part1.certifications,
            achievements=part1.achievements,
            recruiter_insights=part2.recruiter_insights,
            search_tags=part2.search_tags,
            languages=part1.languages,
            resume_summary=part2.resume_summary,
        )
    


# # ----------------------------------------------------------------------------------------------
# # Main Resume Metadata
# # ----------------------------------------------------------------------------------------------

# class ResumeMetadata(BaseModel):
#     """Structured resume analysis output.

#     Field order below is intentional: heavier/higher-priority sections come first,
#     and short/cheap-to-generate fields are placed last. This reduces the chance
#     that a token-budget cutoff truncates the response before required fields
#     (especially search_tags) are generated.
#     """

#     model_config = ConfigDict(extra="forbid")

#     basic_info: BasicInfo = Field(
#         description="Candidate's basic contact and identity information."
#     )
#     education: List[Education] = Field(
#         description="All education records, in reverse chronological order."
#     )
#     experience: List[Experience] = Field(
#         description="All professional experience records, in reverse chronological order."
#     )
#     projects: List[Project] = Field(
#         description="All projects mentioned in the resume."
#     )
#     skills: List[str] = Field(
#         max_length=40,
#         description=(
#             "List of unique skills explicitly mentioned in the resume. "
#             "Include only skills that are directly stated by the candidate in the Skills section "
#             "or elsewhere in the resume. Do not infer, derive, or assume skills based on projects, "
#             "experience, certifications, technologies used, or any other context. "
#             "Preserve the skill names as written in the resume while removing duplicates."
#         ),
#     )
#     certifications: List[Certification] = Field(
#         description="All certifications mentioned in the resume."
#     )
#     achievements: List[Achievement] = Field(
#         max_length=15,
#         description="All notable achievements: awards, hackathons, publications, patents, etc.",
#     )
#     recruiter_insights: List[RecruiterInsight] = Field(
#         max_length=5,
#         description="2-5 evidence-based, job-independent recruiter insights derived from the resume.",
#     )
#     search_tags: List[str] = Field(
#         max_length=20,
#         description=(
#             "10-20 unique, normalized tags that improve candidate search and retrieval. "
#             "Generate tags only from explicit information present in the resume. "
#             "Include technical skills, domains, certifications, industries, tools, "
#             "roles, education specializations, and notable expertise. "
#             "Do not invent or infer tags that are not supported by the resume."
#         ),
#     )
#     languages: List[str] = Field(
#         description="Human languages explicitly mentioned in the resume."
#     )
#     resume_summary: str = Field(
#         description=(
#             "Professional summary exactly as mentioned in the resume (e.g. 'About Me', "
#             "'Summary', 'Profile' section). Empty string if no summary is present. "
#             "Do not generate a new summary."
#         )
#     )