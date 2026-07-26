"""
This file handles database operations for the sessions table.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.dbtype.local_storage.postgres.models.session_model import SessionModel


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
            print(f"Error adding session details: {e}")
            return None


    def update_session_details(
        self,
        session_id: str,
        status: str,
        successful_resumes: int,
        failed_resumes: int,
    ):
        """
        Update session processing details.
        """

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

            self.db.commit()
            self.db.refresh(session)

            return session

        except Exception as e:
            self.db.rollback()
            print(f"Error updating session details: {e}")
            return None


    def delete_session_by_id(self, session_id: str):
        """
        Delete a session using its session ID.
        """

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
            print(f"Error deleting session: {e}")
            return None



    def get_sessions(self):
        """
        Fetch all sessions ordered by creation time (latest first).
        """

        try:
            return (
                self.db.query(SessionModel)
                .order_by(SessionModel.created_at.desc())
                .all()
            )

        except Exception as e:
            print(f"Error fetching sessions: {e}")
            return None
    

    def get_sessions_by_user(self , user_id:str):
        """
        Fetch all sessions ordered by creation time (latest first).
        """

        try:
            return (
                self.db.query(SessionModel)
                .filter(SessionModel.user_id == user_id)
                .order_by(SessionModel.created_at.desc())
                .all()
            )

        except Exception as e:
            print(f"Error fetching sessions: {e}")
            return None