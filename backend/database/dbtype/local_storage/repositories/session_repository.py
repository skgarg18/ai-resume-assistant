"""
This file handles database operations for the sessions table.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.dbtype.local_storage.postgres.models.session_model import SessionModel
from utils.log_utils import get_logger

from datetime import datetime


class SessionRepository:

    def __init__(self, db: Session):
        """
        Initialize the repository with a SQLAlchemy database session.
        """
        self.db = db

    def add_session_details(
        self,
        session_id: str,
        user_id:str,
        session_name: str,
        jd_description: str,
        upload_source: str,
        total_resumes: int,
        rq_job_id: str,
        user_email: str
    ):
        """
        Add a new session to the database.
        """

        logger = get_logger()

        try:
            session = SessionModel(
                session_id=session_id,
                user_id=user_id,
                session_name=session_name,
                job_description=jd_description,
                upload_source=upload_source,
                total_resumes=total_resumes,
                rq_job_id=rq_job_id,
                user_email=user_email
            )

            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            return session

        except Exception as e:
            self.db.rollback()
            logger.error("Error adding session details | error =  {}" , e)
            return None


    def update_session_details(
        self,
        session_id: str,
        status: str,
        successful_resumes: int,
        failed_resumes: int,
        reason:str | None=None,
        email_status:str | None=None
    ):
        """
        Update session processing details.
        """

        logger = get_logger()

        try:
            session = (
                self.db.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .first()
            )

            if session is None:
                return None

            session.status = status
            session.successful_resumes = successful_resumes
            session.failed_resumes = failed_resumes
            session.updated_at = func.now()

            if reason:
                session.reason = reason
            
            if email_status:
                session.email_status = email_status

            self.db.commit()
            self.db.refresh(session)

            return session

        except Exception as e:
            self.db.rollback()
            logger.error("Error updating session details | error={}")
            return None


    def delete_session_by_id(self, session_id: str):
        """
        Delete a session using its session ID.
        """

        logger = get_logger()

        try:
            session = (
                self.db.query(SessionModel)
                .filter(SessionModel.session_id == session_id)
                .first()
            )

            if session is None:
                return None


            # Delete session from database
            self.db.delete(session)
            self.db.commit()

            return session

        except Exception as e:
            self.db.rollback()
            logger.error("Error deleting session | error={}" , e)
            return None



    def get_sessions(self):
        """
        Fetch all sessions ordered by creation time (latest first).
        """

        logger = get_logger()

        try:
            return (
                self.db.query(SessionModel)
                .order_by(SessionModel.created_at.desc())
                .all()
            )

        except Exception as e:
            logger.error("Error fetching sessions | error={}" , e)
            return None
        
    
    def get_session_data_by_session_id(self, session_id: str):
        """
        Fetches session details needed specifically for Excel export generation.
        """

        logger = get_logger()

        try:
            # Query active database model directly
            # Replacing with raw SQLAlchemy model reference matching your system
            
            session_obj = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
            if not session_obj:
                return None

            return {
                "id": str(session_obj.session_id),
                "session_name": session_obj.session_name,
                "job_description": getattr(session_obj, "job_description", "No Job Description Provided"),
                "export_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as exc:
            logger.error(f"Error querying session export data: {exc}")
            raise exc
    

    def get_sessions_by_user(self , user_id:str):
        """
        Fetch all sessions ordered by creation time (latest first).
        """

        logger = get_logger()

        try:
            return (
                self.db.query(SessionModel)
                .filter(SessionModel.user_id == user_id)
                .order_by(SessionModel.created_at.desc())
                .all()
            )

        except Exception as e:
            logger.error("Error fetching session | error={}" , e)
            return None