from sqlalchemy import Column, DateTime, ForeignKey, Text, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func

from database.dbtype.local_storage.postgres.base import Base


class ResumeMetadata(Base):
    __tablename__ = "resume_metadata"

    session_id = Column(
       String,
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id = Column(
        String,
        ForeignKey("resumes.resume_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    # Structured metadata
    basic_info = Column(JSONB, nullable=False)

    education = Column(JSONB, nullable=False, default=list)

    experience = Column(JSONB, nullable=False, default=list)

    projects = Column(JSONB, nullable=False, default=list)

    certifications = Column(JSONB, nullable=False, default=list)

    achievements = Column(JSONB, nullable=False, default=list)

    recruiter_insights = Column(JSONB, nullable=False, default=list)

    # Searchable fields
    skills = Column(ARRAY(Text), nullable=False, default=list)

    languages = Column(ARRAY(Text), nullable=False, default=list)

    search_tags = Column(ARRAY(Text), nullable=False, default=list)

    # Generated summary
    resume_summary = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

