from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    technical_skills: int = Field(
        ge=0,
        le=100,
        description=(
            "Evidence-based alignment score from 0 to 100 "
            "for technical skills."
        )
    )

    professional_experience: int = Field(
        ge=0,
        le=100,
        description=(
            "Evidence-based alignment score from 0 to 100 "
            "for professional experience."
        )
    )

    project_evidence: int = Field(
        ge=0,
        le=100,
        description=(
            "Evidence-based alignment score from 0 to 100 "
            "for project evidence."
        )
    )

    education_and_training: int = Field(
        ge=0,
        le=100,
        description=(
            "Evidence-based alignment score from 0 to 100 "
            "for education and training."
        )
    )

    domain_relevance: int = Field(
        ge=0,
        le=100,
        description=(
            "Evidence-based alignment score from 0 to 100 "
            "for domain relevance."
        )
    )

class ResumeEvaluation(BaseModel):
    score_breakdown: ScoreBreakdown

    summary: list[str] = Field(
        description=(
            "5 to 6 concise recruiter-style evaluation points explaining "
            "the major factors that increased or decreased the candidate's "
            "evaluation scores."
        )
    )

    top_matched_skills: list[str] = Field(
        description=(
            "Up to 8 of the most important skills or technologies "
            "demonstrated by the candidate that match the job description."
        )
    )

    missing_skills: list[str] = Field(
        description=(
            "Up to 5 important skills or technical requirements from "
            "the job description that are not clearly demonstrated "
            "in the resume."
        )
    )
