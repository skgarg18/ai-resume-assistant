from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.dbtype.local_storage.postgres.base import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rq_job_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    session_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    job_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="processing",
        server_default="processing",
    )

    upload_source: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="files",
        server_default="files",
    )

    total_resumes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    successful_resumes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    failed_resumes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_email: Mapped[str] = mapped_column(
        String,
        server_default="",
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String,
        server_default="",
        nullable=True,
    )

    email_status: Mapped[str | None] = mapped_column(
        String,
        server_default="",
        nullable=True,
    )