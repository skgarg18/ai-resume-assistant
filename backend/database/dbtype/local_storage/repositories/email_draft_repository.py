"""
This file handles database operations for the email_drafts table.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.email_drafts_model import EmailDraftModel
from database.dbtype.local_storage.postgres.normalize_response import model_to_dict

class EmailDraftRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_data_email_draft(
        self,
        session_id,
        candidate_name,
        candidate_email,
        subject,
        body,
        status,
        original_prompt,
        meeting_metadata,
    ):
        """
        Add a new email draft.
        """

        try:
            email_draft = EmailDraftModel(
                session_id=session_id,
                candidate_name=candidate_name,
                recipient_email=candidate_email,
                subject=subject,
                body=body,
                status=status,
                original_prompt=original_prompt,
                meeting_metadata=meeting_metadata,
            )

            self.db.add(email_draft)
            self.db.commit()
            self.db.refresh(email_draft)

            # return email_draft

            return model_to_dict(email_draft)


        except Exception as e:
            self.db.rollback()
            print(f"Error uploading email draft data: {e}")
            return None



    def get_data_by_draft_id(self, draft_id: int):
        """
        Fetch an email draft by its ID.
        """

        try:
            draft_response =  (
                self.db.query(EmailDraftModel)
                .filter(EmailDraftModel.id == draft_id)
                .first()
            )

            return model_to_dict(draft_response)

        except Exception as e:
            print(f"Error fetching email draft: {e}")
            return None



    def update_regenerate_email_draft_by_id(
        self,
        draft_id: int,
        subject: str,
        body: str,
        regeneration_count: int,
        updated_at: datetime,
        meeting_metadata: dict | None,
    ):
        """
        Update an email draft after regeneration.
        """

        try:
            draft = (
                self.db.query(EmailDraftModel)
                .filter(EmailDraftModel.id == draft_id)
                .first()
            )

            if draft is None:
                return None

            draft.subject = subject
            draft.body = body
            draft.regeneration_count = regeneration_count
            draft.updated_at = updated_at
            draft.meeting_metadata = meeting_metadata

            self.db.commit()
            self.db.refresh(draft)

            return model_to_dict(draft)

        except Exception as e:
            self.db.rollback()
            print(f"Error updating regenerated email draft: {e}")
            return None




    def update_sent_email_draft(
        self,
        draft_id: int,
        sent_at: datetime,
        updated_at: datetime,
        meeting_metadata: dict | None,
    ):
        """
        Mark an email draft as sent.
        """

        try:
            draft = (
                self.db.query(EmailDraftModel)
                .filter(EmailDraftModel.id == draft_id)
                .first()
            )

            if draft is None:
                return None

            draft.status = "sent"
            draft.sent_at = sent_at
            draft.updated_at = updated_at
            draft.meeting_metadata = meeting_metadata

            self.db.commit()
            self.db.refresh(draft)

            return model_to_dict(draft)

        except Exception as e:
            self.db.rollback()
            print(f"Error updating email sent status: {e}")
            return None