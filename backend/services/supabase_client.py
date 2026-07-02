# services/supabase_client.py

import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SECRET_KEY"]
)

bucket_name = "resume-files"


def store_file_in_bucket(
    file_path: str,
    file_content: bytes
) -> str:

    extension = Path(file_path).suffix.lower()

    content_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    supabase.storage.from_(bucket_name).upload(
        path=file_path,
        file=file_content,
        file_options={
            "content-type": content_types.get(
                extension,
                "application/octet-stream"
            )
        }
    )

    return