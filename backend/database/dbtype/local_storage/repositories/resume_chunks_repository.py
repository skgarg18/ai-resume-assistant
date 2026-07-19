"""
Repository responsible for handling resume chunk storage
and similarity search using persistent ChromaDB.
"""

import shutil
from pathlib import Path

import chromadb
from chromadb.config import Settings


class ResumeChunksRepository:

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(
        self,
        storage_directory: str = "storage/chroma",
    ):
        self.storage_directory = Path(storage_directory)
        self.storage_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Cache one client per session
        self._clients: dict[str, chromadb.PersistentClient] = {}

    # --------------------------------------------------
    # Get Chroma Collection
    # --------------------------------------------------

    def _get_collection(
        self,
        session_id: str,
    ):
        """
        Returns the Chroma collection associated with a session.
        Creates the client/collection if necessary.
        """

        session_directory = (
            self.storage_directory
            / session_id
        )

        session_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        if session_id not in self._clients:
            self._clients[session_id] = chromadb.PersistentClient(
                path=str(session_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                ),
            )

        client = self._clients[session_id]

        return client.get_or_create_collection(
            name="resume_chunks"
        )

    # --------------------------------------------------
    # Store Resume Chunks
    # --------------------------------------------------

    def add_resume_chunks(
        self,
        chunk_rows: list[dict],
    ):
        try:

            if not chunk_rows:
                return True

            collection = self._get_collection(
                chunk_rows[0]["session_id"]
            )

            ids = []
            documents = []
            embeddings = []
            metadatas = []

            for row in chunk_rows:

                ids.append(
                    f'{row["resume_id"]}_{row["chunk_index"]}'
                )

                documents.append(
                    row["chunk_text"]
                )

                embeddings.append(
                    row["embedding"]
                )

                metadatas.append(
                    {
                        "resume_id": row["resume_id"],
                        "candidate_name": row["candidate_name"],
                        "chunk_index": row["chunk_index"],
                    }
                )

            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            return True

        except Exception as e:
            print(f"Error adding resume chunks: {e}")
            return None


    # --------------------------------------------------
    # Delete Resume Chunks
    # --------------------------------------------------

    def delete_resume_chunks_by_session(
        self,
        session_id: str,
    ):
        """
        Delete all Chroma data belonging to a session.
        """

        try:

            session_directory = (
                self.storage_directory
                / session_id
            )

            client = self._clients.pop(
                session_id,
                None,
            )

            if client is None and session_directory.exists():
                client = chromadb.PersistentClient(
                    path=str(session_directory),
                    settings=Settings(
                        anonymized_telemetry=False,
                    ),
                )

            if client is not None:
                try:
                    client.delete_collection(
                        "resume_chunks"
                    )
                except Exception:
                    # Collection may already be deleted
                    pass

                client.close()

            if session_directory.exists():
                shutil.rmtree(session_directory)

            return True

        except Exception as e:
            print(f"Error deleting resume chunks: {e}")
            return None


    # --------------------------------------------------
    # Similarity Search
    # --------------------------------------------------

    def derive_top_resume_chunks_similarity_search(
        self,
        session_id: str,
        candidate_name: str | None,
        query_embedding: list[float],
        match_count: int,
    ):
        """
        Perform similarity search over resume chunks
        for a specific candidate.
        """

        try:

            collection = self._get_collection(
                session_id
            )

            if candidate_name:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=match_count,
                    where={
                        "candidate_name": candidate_name,
                    },
                )

            else:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=match_count,
                )

            normalized_results = []

            documents = results.get(
                "documents",
                [[]],
            )[0]

            metadatas = results.get(
                "metadatas",
                [[]],
            )[0]

            embeddings = (
                results.get(
                    "embeddings",
                    [[]],
                )[0]
                if results.get("embeddings")
                else []
            )

            ids = results.get(
                "ids",
                [[]],
            )[0]

            distances = results.get(
                "distances",
                [[]],
            )[0]

            for i in range(len(documents)):
                metadata = metadatas[i]

                normalized_results.append(
                    {
                        "id": ids[i],
                        "resume_id": metadata.get("resume_id"),
                        "chunk_text": documents[i],
                        "candidate_name": metadata.get("candidate_name"),
                        "chunk_index": metadata.get("chunk_index"),
                        "embedding": (
                            embeddings[i]
                            if embeddings
                            else None
                        ),
                        "distance": (
                            distances[i]
                            if distances
                            else None
                        ),
                    }
                )

            return normalized_results

        except Exception as e:
            print(
                f"Error deriving top resume chunks similarity search: {e}"
            )
            return None