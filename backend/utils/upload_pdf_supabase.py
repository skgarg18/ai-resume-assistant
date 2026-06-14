# storage.py

import uuid
from services.supabase_client import supabase


def upload_pdf(file_bytes: bytes, filename: str, chat_id: str):
    """
    Upload PDF to Supabase Storage
    """

    unique_name = f"{uuid.uuid4()}.pdf"

    storage_path = f"{chat_id}/{unique_name}"

    supabase.storage.from_("resume-files").upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": "application/pdf"
        }
    )

    return {
        "storage_path": storage_path,
        "original_filename": filename
    }