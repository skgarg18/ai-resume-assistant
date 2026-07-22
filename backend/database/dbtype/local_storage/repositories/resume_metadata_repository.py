from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.resume_metadata import ResumeMetadata
from database.dbtype.local_storage.postgres.normalize_response import models_to_dict

class ResumeMetadataRepo:

    
    def __init__(self, db: Session):
        self.db = db    
    
    def add_resume_metadata(
            self , 
            resume_metadata: list[dict]
    ):
        
        """
        Add multiple resume records to the database.
        """

        try:

            resumes = [
                ResumeMetadata(**resume_data)
                for resume_data in resume_metadata
            ]

            self.db.add_all(resumes)
            self.db.commit()

            return resumes

        except Exception as e:
            self.db.rollback()
            print(f"Error adding resume Metadata: {e}")
            return None

