from database.dbtype.supabase.supabase_client import (
    supabase,
    bucket_name
)


from database.dbtype.supabase.repositories.email_draft_repository import EmailDraftRepository
from database.dbtype.supabase.repositories.chat_history_repository import ChatHistoryRepository
from database.dbtype.supabase.repositories.resume_chunks_repository import ResumeChunksRepository
from database.dbtype.supabase.repositories.resume_repository import ResumeRepository
from database.dbtype.supabase.repositories.session_repository import SessionRepository
from database.dbtype.supabase.repositories.users_repository import UserRepository
from database.dbtype.supabase.repositories.files_repository import FilesRepository


email_draft_repo = EmailDraftRepository(supabase)
chat_hist_repo = ChatHistoryRepository(supabase)
resume_chunks_repo = ResumeChunksRepository(supabase)
resume_repo = ResumeRepository(supabase)
session_repo = SessionRepository(supabase)
user_repo = UserRepository(supabase)
files_repo = FilesRepository(supabase , bucket_name)
