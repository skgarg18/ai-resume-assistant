from sqlalchemy import Column, String, Text, DateTime, func

from database.dbtype.local_storage.postgres.base import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)

    session_name = Column(String, nullable=False)
    job_description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )