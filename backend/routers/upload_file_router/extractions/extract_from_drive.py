
from services.supabase_client import supabase
from services.google_drive_service import (
    get_drive_service,
    download_pdf
)

from utils.extract_folder_from_drive_id_link import extract_folder_id_drive

def extract_files_from_drive(
        drive_link: str,):

    # ----------------------------------------------------------
    # Extracting the folder ID
    # ----------------------------------------------------------

    folder_id = extract_folder_id_drive(drive_link)

    # -----------------------------------------------------------
    # Getting refresh token
    # ------------------------------------------------------------

    result = (
        supabase.table("google_integrations")
        .select("refresh_token")
        .eq("user_id", 1)
        .single()
        .execute()
    )

    if not result.data:
        raise Exception(
            "Google Drive not connected"
        )

    refresh_tok = result.data["refresh_token"]


    # -----------------------------------------------------------
    # Creating a google drive client
    # ------------------------------------------------------------

    service = get_drive_service(
        refresh_tok
    )


    # --------------------------------------------------------------
    # retriving files from drive folder
    # --------------------------------------------------------------

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id,name,mimeType)"
    ).execute()

    files_data = []

    for file in results["files"]:

        pdf_bytes = download_pdf(
            service,
            file["id"]
        )

        files_data.append(
            {
                "filename": file["name"],
                "content": pdf_bytes
            }
        )

    return files_data



    
