"""
This file handles database operations for the resumes table.
"""

from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.resume_model import ResumeModel
from database.dbtype.local_storage.postgres.normalize_response import models_to_dict

class ResumeRepository:

    def __init__(self, db: Session):
        self.db = db



    def add_resume_data(
        self,
        resume_data_rows: list[dict],
    ):
        """
        Add multiple resume records to the database.
        """

        try:

            resumes = [
                ResumeModel(**resume_data)
                for resume_data in resume_data_rows
            ]

            self.db.add_all(resumes)
            self.db.commit()

            return resumes

        except Exception as e:
            self.db.rollback()
            print(f"Error adding resume data: {e}")
            return None
        


    def delete_resume_data_by_session(self, session_id: str):
        """
        Delete all resumes belonging to a session.
        """

        try:
            resumes = (
                self.db.query(ResumeModel)
                .filter(ResumeModel.session_id == session_id)
                .all()
            )

            if not resumes:
                return []

            for resume in resumes:
                self.db.delete(resume)

            self.db.commit()

            return resumes

        except Exception as e:
            self.db.rollback()
            print(f"Error deleting resume data: {e}")
            return None



    def get_resume_data(self, session_id: str):
        """
        Fetch resumes for a session ordered by score (highest first).
        """

        try:
            resumes = (
                self.db.query(ResumeModel)
                .filter(ResumeModel.session_id == session_id)
                .all()
            )
            
        
            return models_to_dict(resumes)

        except Exception as e:
            print(f"Error fetching resume data: {e}")
            return None
        

    



    def get_candidate_emails(
        self,
        session_id: str,
        candidate_name: str,
    ) -> list[str] | None:
        """
        Fetch all email IDs corresponding to a candidate name
        within a session.
        """
    
        try:
            resumes = (
                self.db.query(ResumeModel)
                .filter(
                    ResumeModel.session_id == session_id,
                    ResumeModel.name.ilike(candidate_name),
                )
                .all()
            )
    
            if not resumes:
                return []
    
            return [
                resume.email
                for resume in resumes
                if resume.email
            ]
    
        except Exception as e:
            print(f"Error fetching candidate emails: {e}")
            return None