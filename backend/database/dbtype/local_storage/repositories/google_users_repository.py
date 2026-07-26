"""
This file handles database operations for the users table.
"""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.google_user_model import GoogleUserModel
from database.dbtype.local_storage.postgres.normalize_response import model_to_dict


class GoogleUserRepository:

    def __init__(self, db: Session):
        self.db = db

    def update_or_insert_user_data(
        self,
        session_id:str,
        google_id: str,
        email: str,
        name: str,
        picture: str,
        refresh_token: str,
    ):
        """
        Insert a new user or update an existing one based on google_id.
        """

        try:
            stmt = (
                insert(GoogleUserModel)
                .values(
                    session_id=session_id,
                    google_id=google_id,
                    email=email,
                    name=name,
                    picture=picture,
                    refresh_token=refresh_token,
                )
                .on_conflict_do_update(
                    index_elements=["google_id"],
                    set_={
                        "email": email,
                        "name": name,
                        "picture": picture,
                        "refresh_token": refresh_token,
                    },
                )
            )

            self.db.execute(stmt)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            print(f"Error upserting user data for {email}: {e}")
            return None


    def get_refresh_token_by_id(self, user_id: int):
        """
        Fetch the refresh token for a user.
        """

        try:
            user = (
                self.db.query(GoogleUserModel)
                .filter(GoogleUserModel.user_id == user_id)
                .first()
            )

            return user.refresh_token if user else None

        except Exception as e:
            print(f"Error fetching refresh token: {e}")
            return None


    def get_user_data_by_user_id(self , user_id:int):
        """
        Fetch user data by user id
        """

        try:
            user_data = (
                self.db.query(GoogleUserModel)
                .filter(GoogleUserModel.user_id == user_id)
                .first()
            )

            return user_data
        
        except Exception as e:
            print(f"Error fetching user data for user_id {user_id}: {e}")
            return None





    def get_user_data_by_google_id(self, google_id: str):
        """
        Fetch user details using the Google ID.
        """

        try:
            user_data =  (
                self.db.query(GoogleUserModel)
                .filter(GoogleUserModel.google_id == google_id)
                .first()
            )

            return model_to_dict(user_data)

        except Exception as e:
            print(f"Error fetching user data for google_id {google_id}: {e}")
            return None