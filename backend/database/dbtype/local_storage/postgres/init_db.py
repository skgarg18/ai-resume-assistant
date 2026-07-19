from database.dbtype.local_storage.postgres.postgres_client import engine
from database.dbtype.local_storage.postgres.base import Base

# Import all models
from database.dbtype.local_storage.postgres.models.session_model import SessionModel
from database.dbtype.local_storage.postgres.models.resume_model import ResumeModel
from database.dbtype.local_storage.postgres.models.chat_history_model import ChatHistoryModel
from database.dbtype.local_storage.postgres.models.email_drafts_model import EmailDraftModel
from database.dbtype.local_storage.postgres.models.user_model import UserModel

def init_db():
    Base.metadata.create_all(bind=engine)