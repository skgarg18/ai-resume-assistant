from database.dbtype.local_storage.postgres.postgres_client import SessionLocal

from database.dbtype.local_storage.repositories.email_draft_repository import EmailDraftRepository
from database.dbtype.local_storage.repositories.chat_history_repository import ChatHistoryRepository
from database.dbtype.local_storage.repositories.resume_chunks_repository import ResumeChunksRepository
from database.dbtype.local_storage.repositories.resume_repository import ResumeRepository
from database.dbtype.local_storage.repositories.session_repository import SessionRepository
from database.dbtype.local_storage.repositories.users_repository import UserRepository
from database.dbtype.local_storage.repositories.files_repository import FilesRepository
from database.dbtype.local_storage.repositories.resume_metadata_repository import ResumeMetadataRepo

# --------------------------------------------------
# Database Session
# --------------------------------------------------

db = SessionLocal()


# --------------------------------------------------
# Storage Paths
# --------------------------------------------------

FILES_STORAGE_PATH = "database/dbtype/local_storage/files"
CHROMA_STORAGE_PATH = "database/dbtype/local_storage/chroma_db_chunks"


# --------------------------------------------------
# Repository Instances
# --------------------------------------------------

email_draft_repo = EmailDraftRepository(db)
chat_hist_repo = ChatHistoryRepository(db)
resume_repo = ResumeRepository(db)
session_repo = SessionRepository(db)
user_repo = UserRepository(db)
resume_metadata_repo = ResumeMetadataRepo(db)

files_repo = FilesRepository(FILES_STORAGE_PATH)
resume_chunks_repo = ResumeChunksRepository(CHROMA_STORAGE_PATH)