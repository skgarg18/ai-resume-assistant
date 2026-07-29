"""
Repository for the chat_history table.

Design:
- One row per session.
- Each row contains a JSON array (messages).
- Every new interaction is appended to the messages list.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.chat_history_model import (
    ChatHistoryModel,
)


class ChatHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_chat_history(
        self,
        session_id: str,
        message_type: str,
        user_message: str,
        details: dict | None = None,
        assistant_message: str | None = None,
        name: str | None = None,
        email_ids: list[str] | None = None,
        selected_email: str | None = None,
        email_subject: str | None = None,
        email_body: str | None = None,
        draft_id: str | None = None,
        email_meeting_metadata: dict | None = None,
        cc_emails: list[str] | None = None,
        bcc_emails: list[str] | None = None,

    ):
        """
        Adds a new interaction to the chat history.

        If the session does not exist, a new row is created.
        Otherwise, the interaction is appended to the existing
        messages list.
        """

        try:

            # ----------------------------------------------------
            # Create interaction object
            # ----------------------------------------------------

            interaction = {
                "message_type": message_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "name": name,
                "user_message": user_message,
                "assistant_message": assistant_message,
            }

            # Add email-specific fields only for email interactions
            if message_type == "email":
                interaction.update(
                    {
                        "email_ids": email_ids or [],
                        "selected_email": selected_email,
                        "email_subject": email_subject,
                        "email_body": email_body,
                        "draft_id": draft_id,
                        "email_meeting_metadata": email_meeting_metadata,
                        "cc_emails": cc_emails or [],
                        "bcc_emails": bcc_emails or [],
                    }
                )

            if details is not None:
                interaction.update(
                    {
                        "details": details
                    }
                )

            # ----------------------------------------------------
            # Check whether this session already has chat history
            # ----------------------------------------------------

            history = (
                self.db.query(ChatHistoryModel)
                .filter(ChatHistoryModel.session_id == session_id)
                .first()
            )

            # ----------------------------------------------------
            # Create new row if session does not exist
            # ----------------------------------------------------

            if history is None:

                history = ChatHistoryModel(
                    session_id=session_id,
                    messages=[interaction],
                )

                self.db.add(history)

            # ----------------------------------------------------
            # Otherwise append to existing history
            # ----------------------------------------------------

            else:

                history.messages.append(interaction)

            self.db.commit()

            return history

        except Exception as e:

            self.db.rollback()

            print(f"Error adding chat history: {e}")

            return None


    def get_chat_history_by_session_id(
        self,
        session_id: str,
    ):
        """
        Returns the complete chat history for a session.

        Returns:
            list[dict] : Chat interactions
            []         : Session exists but no messages
            None       : Database error
        """

        try:

            history = (
                self.db.query(ChatHistoryModel)
                .filter(ChatHistoryModel.session_id == session_id)
                .first()
            )

            if history is None:
                return []

            return history.messages

        except Exception as e:

            print(
                f"Error fetching chat history for session "
                f"{session_id}: {e}"
            )

            return None

    def delete_chat_history(
        self,
        session_id: str,
    ):
        """
        Deletes the complete chat history for a session.
        """

        try:

            deleted_rows = (
                self.db.query(ChatHistoryModel)
                .filter(ChatHistoryModel.session_id == session_id)
                .delete()
            )

            self.db.commit()

            return deleted_rows > 0

        except Exception as e:

            self.db.rollback()

            print(
                f"Error deleting chat history for session "
                f"{session_id}: {e}"
            )

            return False