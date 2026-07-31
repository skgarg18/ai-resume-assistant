"""
This file handles database operations for the resumes table.
"""

from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.resume_model import ResumeModel
from database.dbtype.local_storage.postgres.normalize_response import models_to_dict

from utils.log_utils import get_logger

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
        logger = get_logger()

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
            logger.error("Error adding resume data | error =  {}" , e)
            return None
        


    def delete_resume_data_by_session(self, session_id: str):
        """
        Delete all resumes belonging to a session.
        """
        logger = get_logger()

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
            logger.error("Error deleting resume data | error={}" , e)
            return None



    def get_evaluation_resume_data(self , session_id:str):
        """
            Fetches resumes evaluation data from resume table corresponsing to a session
        """

        logger = get_logger()

        try:
            resumes = (
                self.db.query(
                    ResumeModel.resume_id,
                    ResumeModel.name,
                    ResumeModel.email,
                    ResumeModel.contact,
                    ResumeModel.score,
                    ResumeModel.overall_score,
                    ResumeModel.summary,
                    ResumeModel.matched_skills,
                    ResumeModel.missing_skills,
                    ResumeModel.file_url,
                    ResumeModel.created_at,
                    ResumeModel.recruiter_insights
                )
                .filter(ResumeModel.session_id == session_id)
                .all()
            )
    
            return [
                {
                    "resume_id": row.resume_id,
                    "name": row.name,
                    "email": row.email,
                    "contact": row.contact,
                    "score": row.score,
                    "overall_score": row.overall_score,
                    "summary": row.summary,
                    "matched_skills": row.matched_skills,
                    "missing_skills": row.missing_skills,
                    "file_url": row.file_url,
                    "created_at": row.created_at,
                    "recruiter_insights": row.recruiter_insights
                }
                for row in resumes
            ]
    
        except Exception as e:
            logger.error("Error fetching resume data | error={}" , e)
            return None



    def get_resume_data(self, session_id: str):
        """
        Fetch resumes for a session ordered by score (highest first).
        """

        logger = get_logger()

        try:
            resumes = (
                self.db.query(ResumeModel)
                .filter(ResumeModel.session_id == session_id)
                .all()
            )
            
        
            return models_to_dict(resumes)

        except Exception as e:
            logger.error("Error fetching resume data | error={}" , e)
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

        logger = get_logger()
    
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
            logger.error("Error fetching candidate emails | error={}" , e)
            return None
        

    
    def get_resume_data_by_name(
        self,
        session_id: str,
        candidate_name: str,
    ) -> list[ResumeModel] | None:
        """
        Fetch all candidates matching the given name
        within a session.
        """

        logger = get_logger()

        try:
            resumes = (
                self.db.query(ResumeModel)
                .filter(
                    ResumeModel.session_id == session_id,
                    ResumeModel.name.ilike(f"%{candidate_name}%"),
                )
                .order_by(ResumeModel.name)
                .all()
            )

            return resumes

        except Exception as e:
            logger.error(
                "Error fetching candidates by name | session_id={} | candidate_name={} | error={}",
                session_id,
                candidate_name,
                e,
            )
            return None
        
    
    def get_resume_data_by_resume_id(
            self,
            session_id:str,
            resume_id:str
    ):
        """
        Fetch a candidate by resume ID within a session.
        """

        logger = get_logger()

        try:
            resume = (
                self.db.query(ResumeModel)
                .filter(
                    ResumeModel.session_id == session_id,
                    ResumeModel.resume_id == resume_id,
                )
                .first()
            )

            return resume

        except Exception as e:
            logger.error(
                "Error fetching candidates by name | session_id={} | resume_id={} | error={}",
                session_id,
                resume_id,
                e,
            )
            return None        