"""
This file handles database operations for the chat_history table.
"""

from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.chat_history_model import ChatHistoryModel


class ChatHistoryRepository:

    def __init__(self, db: Session):
        self.db = db


    def add_chat_history(
        self,
        session_id: str,
        message_type: str,
        user_message: str,
        assistant_message: str | None = None,
        email_id: str | None = None,
        email_subject: str | None = None,
        email_body: str | None = None,
        draft_id: int | None = None,
        email_meeting_metadata: dict | None = None,
    ):
        """
        Add a chat history record to the database.
        """

        try:
            chat_history = ChatHistoryModel(
                session_id=session_id,
                message_type=message_type,
                user_message=user_message,
                assistant_message=assistant_message,
                email_id=email_id,
                email_subject=email_subject,
                email_body=email_body,
                draft_id=draft_id,
                email_meeting_metadata=email_meeting_metadata,
            )

            self.db.add(chat_history)
            self.db.commit()
            self.db.refresh(chat_history)

            return chat_history

        except Exception as e:
            self.db.rollback()
            print(f"Error adding chat history: {e}")
            return None


    def get_chat_history_by_session_id(self, session_id: str):
        """
        Fetch all chat messages for a session ordered by creation time.
        """

        try:
            return (
                self.db.query(ChatHistoryModel)
                .filter(ChatHistoryModel.session_id == session_id)
                .order_by(ChatHistoryModel.created_at.asc())
                .all()
            )

        except Exception as e:
            print(
                f"Error fetching chat history for session {session_id}: {e}"
            )
            return None