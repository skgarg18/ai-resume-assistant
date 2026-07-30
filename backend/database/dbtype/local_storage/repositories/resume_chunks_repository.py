"""
Repository responsible for handling resume chunk storage
and similarity search using persistent ChromaDB.
"""

import shutil
import gc
import time
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

    # --------------------------------------------------
    # Get Chroma Collection
    # --------------------------------------------------

    def _get_collection(
        self,
        session_id: str,
    ):
        """
        Returns a Chroma collection for the session.
        """
        session_directory = self.storage_directory / session_id
        session_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        client = chromadb.PersistentClient(
            path=str(session_directory),
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )

        collection = client.get_or_create_collection(
            name="resume_chunks",
            metadata={
                "hnsw:space": "cosine"
            }
        )

        return client, collection

    # --------------------------------------------------
    # Store Resume Chunks
    # --------------------------------------------------

    def add_resume_chunks(
        self,
        chunk_rows: list[dict],
    ):
        if not chunk_rows:
            return True

        client = None
        collection = None

        try:
            client, collection = self._get_collection(
                chunk_rows[0]["session_id"]
            )

            ids = []
            documents = []
            embeddings = []
            metadatas = []

            for row in chunk_rows:
                ids.append(f'{row["resume_id"]}_{row["chunk_index"]}')
                documents.append(row["chunk_text"])
                embeddings.append(row["embedding"])

                # SAFE METADATA: ChromaDB does not accept None values.
                # We filter out any None keys before appending.
                raw_metadata = {
                    "resume_id": row.get("resume_id"),
                    "candidate_name": row.get("candidate_name"),
                    "chunk_index": row.get("chunk_index"),
                }
                clean_metadata = {k: v for k, v in raw_metadata.items() if v is not None}
                metadatas.append(clean_metadata)

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

        finally:
            # Guarantees locks are released even if collection.add() fails
            if client:
                client.clear_system_cache()
                del client
            if collection:
                del collection
            gc.collect()

    # --------------------------------------------------
    # Delete Resume Chunks
    # --------------------------------------------------

    def delete_resume_chunks_by_session(
        self,
        session_id: str,
    ):
        session_directory = self.storage_directory / session_id
        if not session_directory.exists():
            return True

        client = None
        try:
            client = chromadb.PersistentClient(
                path=str(session_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                ),
            )

            try:
                client.delete_collection("resume_chunks")
            except Exception:
                pass

        except Exception as e:
            print(f"Error connecting to DB for deletion: {e}")
            return None

        finally:
            if client:
                client.clear_system_cache()
                del client
            gc.collect()

        # Retry loop for directory deletion (now safer since 'finally' freed the locks)
        last_error = None
        for i in range(5):
            try:
                shutil.rmtree(session_directory)
                return True
            except Exception as e:
                last_error = e
                print(f"Attempt {i + 1} failed: {type(e).__name__}: {e}")
                gc.collect()
                time.sleep(0.5)

        print(f"Unable to delete {session_directory}: {last_error}")
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
        client = None
        collection = None
    
        try:
        
            client, collection = self._get_collection(session_id)
    
            where_clause = {}
            if candidate_name:
                where_clause = {
                    "candidate_name": candidate_name
                }
    
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=match_count,
                where=where_clause if where_clause else None,
            )
    
            normalized_results = []
    
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            embeddings = (
                results.get("embeddings", [[]])[0]
                if results.get("embeddings")
                else []
            )
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]
    
            for i in range(len(documents)):
            
                metadata = metadatas[i] if metadatas else {}
    
                distance = (
                    distances[i]
                    if distances
                    else None
                )
    
                cosine_similarity = (
                    1 - distance
                    if distance is not None
                    else None
                )
    
                normalized_results.append(
                    {
                        "id": ids[i],
                        "resume_id": metadata.get("resume_id"),
                        "candidate_name": metadata.get("candidate_name"),
                        "chunk_index": metadata.get("chunk_index"),
                        "chunk_text": documents[i],
                        "embedding": (
                            embeddings[i]
                            if embeddings
                            else None
                        ),
                        "distance": distance,
                        "cosine_similarity": cosine_similarity,
                    }
                )
    
            #
            # Highest similarity first.
            #
            normalized_results.sort(
                key=lambda x: x["cosine_similarity"],
                reverse=True,
            )
    
            return normalized_results
    
        except Exception as e:
        
            print(
                f"Error deriving top resume chunks similarity search: {e}"
            )
    
            return None
    
        finally:
        
            if client:
                client.clear_system_cache()
                del client
    
            if collection:
                del collection
    
            gc.collect()

    
    def derive_top_resume_chunks_resume_id(
        self,
        session_id: str,
        resume_id: str,
        query_embedding: list[float],
        match_count: int,
    ):
        client = None
        collection = None

        try:
            client, collection = self._get_collection(session_id)

            where_clause = {}
            if resume_id:
                where_clause = {"resume_id": resume_id}

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=match_count,
                where=where_clause if where_clause else None,
            )

            normalized_results = []

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            embeddings = (
                results.get("embeddings", [[]])[0]
                if results.get("embeddings")
                else []
            )
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]

            

            for i in range(len(documents)):
                metadata = metadatas[i] if metadatas else {}

                distance = distances[i] if distances else None

                cosine_similarity = (
                    1 - distance
                    if distance is not None
                    else None
                )

                normalized_results.append(
                    {
                        "id": ids[i],
                        "resume_id": metadata.get("resume_id"),
                        "candidate_name": metadata.get("candidate_name"),
                        "chunk_index": metadata.get("chunk_index"),
                        "chunk_text": documents[i],
                        "embedding": embeddings[i] if embeddings else None,
                        "distance": distances[i] if distances else None,
                        "cosine_similarity": cosine_similarity,
                    }
                )
            
            normalized_results.sort(
                key=lambda x: x["cosine_similarity"],
                reverse=True,
            )

            return normalized_results

        except Exception as e:
            print(f"Error deriving top resume chunks similarity search: {e}")
            return None

        finally:
            if client:
                client.clear_system_cache()
                del client
            if collection:
                del collection
            gc.collect()
    


    # --------------------------------------------------
    # Primitive Methods for Hybrid Search
    # --------------------------------------------------

    def get_all_session_chunks(self, session_id: str) -> dict:
        """Fetches raw documents and metadatas for BM25 indexing."""
        client, collection = None, None
        try:
            client, collection = self._get_collection(session_id)
            return collection.get(include=["documents", "metadatas"])
        finally:
            if client:
                client.clear_system_cache()
                del client
            if collection:
                del collection
            gc.collect()

    def query_vector_nearest_neighbors(
        self, session_id: str, query_embedding: list[float], n_results: int
    ) -> dict:
        """Executes raw vector search against ChromaDB."""
        client, collection = None, None
        try:
            client, collection = self._get_collection(session_id)
            return collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )
        finally:
            if client:
                client.clear_system_cache()
                del client
            if collection:
                del collection
            gc.collect()