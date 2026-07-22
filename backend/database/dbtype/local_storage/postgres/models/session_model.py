from sqlalchemy import Column, String, Text, DateTime, Integer, func

from database.dbtype.local_storage.postgres.base import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)

    rq_job_id = Column(String, nullable=False)

    session_name = Column(String, nullable=False)
    job_description = Column(Text)

    status = Column(
        String,
        nullable=False,
        default="processing",
        server_default="processing",
    )

    upload_source = Column(
        String,
        nullable=False,
        default="files",
        server_default="files",
    )

    total_resumes = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    successful_resumes = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    failed_resumes = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )