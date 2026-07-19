from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

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

    score: Mapped[float] = mapped_column(Float)

    summary: Mapped[list[str]] = mapped_column(JSONB)

    matched_skills: Mapped[list] = mapped_column(JSONB)

    missing_skills: Mapped[list] = mapped_column(JSONB)

    file_url: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def to_dict(self):
        return {
            "resume_id": self.resume_id,
            "session_id": self.session_id,
            "name": self.name,
            "email": self.email,
            "contact": self.contact,
            "score": self.score,
            "summary": self.summary,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "file_url": self.file_url,
            "created_at": self.created_at,
        }