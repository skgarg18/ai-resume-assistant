from datetime import datetime

from sqlalchemy import DateTime , ForeignKey,  String, Text, func, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from database.dbtype.local_storage.postgres.base import Base



class ResumeModel(Base):
    __tablename__ = "resumes"

    resume_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    contact: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Structured metadata
    basic_info: Mapped[dict] = mapped_column(
        JSONB, 
        nullable=False
    )

    score: Mapped[dict[str,int]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
        )
    
    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    summary: Mapped[list[str]] = mapped_column(JSONB)

    matched_skills: Mapped[list] = mapped_column(JSONB)

    missing_skills: Mapped[list] = mapped_column(JSONB)

    file_url: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    education: Mapped[list[dict]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list
    )

    experience: Mapped[list[dict]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list
    )

    projects: Mapped[list[dict]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list
    )

    certifications: Mapped[list[dict]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list
    )

    achievements: Mapped[list[dict]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list
    )

    recruiter_insights: Mapped[list[str]] = mapped_column(
        JSONB, 
        nullable=False, 
        default=list
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(Text), 
        nullable=False, 
        default=list
    )

    languages: Mapped[list[str]] = mapped_column(
        ARRAY(Text), 
        nullable=False, 
        default=list
    )

    search_tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text), 
        nullable=False, 
        default=list
    )

    resume_summary: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )


    def to_dict(self):
        return {
            "resume_id": self.resume_id,
            "session_id": self.session_id,
            "name": self.name,
            "email": self.email,
            "contact": self.contact,
            "basic_info": self.basic_info,
            "score": self.score,
            "overall_score" : self.overall_score,
            "summary": self.summary,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "education": self.education,
            "experience": self.experience,
            "projects": self.projects,
            "certifications": self.certifications,
            "achievements": self.achievements,
            "recruiter_insights": self.recruiter_insights,
            "skills": self.skills,
            "languages": self.languages,
            "search_tags": self.search_tags,
            "resume_summary": self.resume_summary,
            "file_url": self.file_url,
            "created_at": self.created_at,
        }