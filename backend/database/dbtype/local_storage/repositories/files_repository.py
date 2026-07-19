"""
Repository responsible for handling local file storage.
"""

from pathlib import Path
import shutil


class FilesRepository:
    """
    Repository for storing and deleting files
    from the local storage directory.
    """

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        storage_directory: str = "storage",
    ):
        """
        Args:
            storage_directory: Root directory where all files are stored.
        """

        self.storage_directory = Path(storage_directory)

        # Create storage directory if it doesn't exist
        self.storage_directory.mkdir(parents=True, exist_ok=True)





    # --------------------------------------------------
    # Store a file locally
    # --------------------------------------------------

    def store_file(
        self,
        file_path: str,
        file_content: bytes,
    ) -> bool:
        """
        Stores a file in the local storage directory.

        Args:
            file_path: Relative path where the file will be stored.
                       Example:
                           resumes/<session_id>/resume.pdf

            file_content: File content as bytes.

        Returns:
            True if the file is stored successfully,
            otherwise False.
        """

        try:
            full_path = self.storage_directory / file_path

            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, "wb") as file:
                file.write(file_content)

            return True

        except Exception as e:
            print(f"Error storing file locally: {e}")
            return False




    # --------------------------------------------------
    # Delete all files belonging to a session
    # --------------------------------------------------

    def delete_session_files(
        self,
        session_id: str,
    ) -> bool:
        """
        Deletes all files belonging to a session.

        Example:
            storage/
                resumes/
                    session123/
                        resume1.pdf
                        resume2.pdf

        Args:
            session_id: Session whose files should be removed.

        Returns:
            True if deletion succeeds (or the folder does not exist),
            otherwise False.
        """

        try:
            session_directory = (
                self.storage_directory
                / session_id
            )

            # Nothing to delete
            if not session_directory.exists():
                return True

            # Delete the entire session directory
            shutil.rmtree(session_directory)

            return True

        except Exception as e:
            print(f"Error deleting session files: {e}")
            return False



    # --------------------------------------------------
    # Generate file URL
    # --------------------------------------------------

    def get_signed_url(
        self,
        file_path: str,
        base_url: str = "http://localhost:8000",
    ) -> str:
        """
        Generate a public URL for a locally stored file.

        Args:
            file_path: Relative file path stored in the database.
                       Example:
                           resumes/session123/resume.pdf

            base_url: Backend base URL.

        Returns:
            URL that can be used by the frontend.
        """

        return f"{base_url}/files/{file_path}"