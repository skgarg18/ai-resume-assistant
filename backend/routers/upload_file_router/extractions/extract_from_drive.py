import logging

from fastapi import HTTPException

from services.google_drive_service import (
    get_drive_service,
    download_pdf,
)

from utils.extract_folder_from_drive_id_link import (
    extract_folder_id_drive,
)

logger = logging.getLogger(__name__)


def extract_files_from_drive(
    drive_link: str,
    user_data,
):
    """
    Extract all supported files from a Google Drive folder.
    """

    logger.info("Starting Google Drive extraction")

    # ----------------------------------------------------------
    # Extract folder ID
    # ----------------------------------------------------------
    try:
        folder_id = extract_folder_id_drive(drive_link)

        logger.info(
            "Drive folder ID extracted successfully | folder_id=%s",
            folder_id,
        )

    except Exception as e:

        logger.exception("Invalid Google Drive folder link")

        raise HTTPException(
            status_code=400,
            detail="Invalid Google Drive folder link.",
        ) from e

    # ----------------------------------------------------------
    # Get refresh token
    # ----------------------------------------------------------
    refresh_token = user_data.refresh_token

    if not refresh_token:

        logger.error(
            "Refresh token not found for user_id=%s",
            user_data.user_id,
        )

        raise HTTPException(
            status_code=401,
            detail="Google account is not connected. Please reconnect your Google account.",
        )

    logger.info(
        "Refresh token retrieved successfully | user_id=%s",
        user_data.user_id,
    )

    # ----------------------------------------------------------
    # Create Google Drive service
    # ----------------------------------------------------------
    try:

        service = get_drive_service(refresh_token)

        logger.info("Google Drive service created successfully")

    except Exception as e:

        logger.exception("Failed to create Google Drive service")

        raise HTTPException(
            status_code=401,
            detail="Failed to authenticate with Google Drive. Please reconnect your Google account.",
        ) from e

    # ----------------------------------------------------------
    # Retrieve files from folder
    # ----------------------------------------------------------
    try:

        results = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents",
                fields="files(id,name,mimeType)",
            )
            .execute()
        )

        logger.info(
            "Retrieved %d files from Drive folder",
            len(results.get("files", [])),
        )

    except Exception as e:

        logger.exception("Failed to list files from Google Drive")

        raise HTTPException(
            status_code=400,
            detail="Unable to access the specified Google Drive folder.",
        ) from e

    files = results.get("files", [])

    if not files:

        logger.warning(
            "Drive folder is empty | folder_id=%s",
            folder_id,
        )

        raise HTTPException(
            status_code=400,
            detail="The selected Google Drive folder is empty.",
        )

    # ----------------------------------------------------------
    # Download files
    # ----------------------------------------------------------
    files_data = []

    for file in files:

        try:

            pdf_bytes = download_pdf(
                service,
                file["id"],
            )

            files_data.append(
                {
                    "filename": file["name"],
                    "content": pdf_bytes,
                }
            )

            logger.info(
                "Downloaded file successfully | filename=%s",
                file["name"],
            )

        except Exception:

            logger.exception(
                "Failed to download file | filename=%s",
                file.get("name"),
            )

            # Continue processing remaining files
            continue

    if not files_data:

        logger.error(
            "Failed to download any files from Drive folder | folder_id=%s",
            folder_id,
        )

        raise HTTPException(
            status_code=400,
            detail="No valid files could be downloaded from the selected Drive folder.",
        )

    logger.info(
        "Google Drive extraction completed successfully | downloaded_files=%d",
        len(files_data),
    )

    return files_data