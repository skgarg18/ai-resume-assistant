"""
SQLAlchemy model for the chat_history table.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database.dbtype.local_storage.postgres.base import Base


class ChatHistoryModel(Base):
    __tablename__ = "chat_history"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Foreign Key
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message Information
    message_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    user_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    assistant_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Email Details
    email_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email_subject: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    email_body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    draft_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    email_meeting_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )