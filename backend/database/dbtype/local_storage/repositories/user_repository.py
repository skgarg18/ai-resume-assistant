from sqlalchemy.orm import Session

from database.dbtype.local_storage.postgres.models.user_model import UserModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    
    def create_user(self ,
                    email:str,
                    password_hash:str,
                    role:str,
                    is_active
    ):
        
        try:
            user = UserModel(
                email=email,
                password_hash=password_hash,
                role=role,
                is_active=is_active,
            )

            self.db.add(user)
            self.db.commit()

            return True
        
        except Exception:
            return False


    def get_user_by_id(self, user_id: str) -> UserModel | None:
        try:
            return (
                self.db.query(UserModel)
                .filter(UserModel.id == user_id)
                .first()
            )
        except Exception:
            return None


    def get_user_by_email(self, email: str) -> UserModel | None:
        try:
            return (
                self.db.query(UserModel)
                .filter(UserModel.email == email)
                .first()
            )
        except Exception:
            return None

    def get_all_users(self) -> list[UserModel] | None:
        try:
            return (
                self.db.query(UserModel)
                .order_by(UserModel.created_at.desc())
                .all()
            )
        except Exception:
            return None