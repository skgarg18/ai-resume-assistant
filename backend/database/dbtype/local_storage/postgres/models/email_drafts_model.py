from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

from database.dbtype.local_storage.postgres.base import Base


class EmailDraftModel(Base):
    __tablename__ = "email_drafts"

    draft_id: Mapped[str] = mapped_column(
        primary_key=True,
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    candidate_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    candidate_email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    original_prompt : Mapped[str] = mapped_column(
        Text,
        nullable = False,
    )

    cc_emails: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list,
    )

    bcc_emails: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list,
    )

    # Number of times the draft was regenerated
    regeneration_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Draft creation time
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Last modification time
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    # Time when email was successfully sent
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

