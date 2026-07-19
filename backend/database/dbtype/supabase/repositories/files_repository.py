"""
Repository responsible for handling file operations
in the Supabase Storage bucket.
"""

from pathlib import Path


class FilesRepository:
    """
    Repository for uploading and deleting files
    from the configured Supabase Storage bucket.
    """

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        supabase,
        bucket_name: str,
    ):
        self.client = supabase
        self.bucket_name = bucket_name





    # --------------------------------------------------
    # Upload a file to the storage bucket
    # --------------------------------------------------

    def store_file(
        self,
        file_path: str,
        file_content: bytes,
    ) -> bool:
        """
        Uploads a file to the configured Supabase bucket.

        Args:
            file_path: Storage path where the file will be stored.
                       Example: session_id/resume.pdf
            file_content: File content as bytes.

        Returns:
            True if upload succeeds, otherwise False.
        """

        try:
            extension = Path(file_path).suffix.lower()

            content_types = {
                ".pdf": "application/pdf",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }

            self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_types.get(
                        extension,
                        "application/octet-stream",
                    )
                },
            )

            return True

        except Exception as e:
            print(f"Error uploading file to storage bucket: {e}")
            return False




    # --------------------------------------------------
    # Delete all files belonging to a session
    # --------------------------------------------------

    def delete_session_files(
        self,
        session_id: str,
    ) -> bool:
        """
        Deletes every file stored under a session folder.

        Example:
            session123/
                resume1.pdf
                resume2.pdf

        Args:
            session_id: Session whose files should be removed.

        Returns:
            True if deletion succeeds (or no files exist),
            otherwise False.
        """

        try:
            bucket = self.client.storage.from_(self.bucket_name)

            # List all files inside the session folder
            files = bucket.list(session_id)

            # Build complete storage paths for deletion
            file_paths = [
                f"{session_id}/{file['name']}"
                for file in files
                if file.get("name")
            ]

            # Nothing to delete
            if not file_paths:
                return True

            # Delete all files in a single request
            bucket.remove(file_paths)

            return True

        except Exception as e:
            print(f"Error deleting session files from storage bucket: {e}")
            return False
        



    # --------------------------------------------------
    # Generate a signed URL for a file
    # --------------------------------------------------
    
    def get_signed_url(
        self,
        file_path: str,
        expires_in: int = 3600,
    ):
        """
            Generate a temporary signed URL for accessing a file
            stored in the private Supabase Storage bucket.
        """


        try:
            signed_url =  (
                self.client.storage
                .from_("resume-files")
                .create_signed_url(file_path, expires_in)
            )

            return signed_url["signedURL"]
        
        except Exception as e:
            print(f"Error creating signed URL: {e}")
            return None