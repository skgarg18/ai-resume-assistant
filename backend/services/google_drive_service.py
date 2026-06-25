import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import io

from googleapiclient.http import (
    MediaIoBaseDownload
)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def get_drive_service(
    refresh_token
):

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri=
            "https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    return build(
        "drive",
        "v3",
        credentials=creds
    )



def download_pdf(
    service,
    file_id
):

    request = service.files().get_media(
        fileId=file_id
    )

    file_stream = io.BytesIO()

    downloader = MediaIoBaseDownload(
        file_stream,
        request
    )

    done = False

    while not done:
        _, done = downloader.next_chunk()

    file_stream.seek(0)

    return file_stream.read()