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

from utils.log_utils import get_logger


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
    


    def derive_resume_chunks_distance_threshold(
        self,
        session_id: str,
        query_embedding: list[float],
        distance_threshold: float = 0.30,
        max_results: int = 300,
    ):
        """
        Retrieve resume chunks whose embedding distance is within the
        specified threshold.

        Since ChromaDB does not support distance filtering during query,
        we retrieve a large number of nearest neighbours and filter them
        afterwards.

        Returns chunks sorted by increasing distance.
        """

        client = None
        collection = None
        logger = get_logger()

        try:

            client, collection = self._get_collection(session_id)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
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
                logger.info(
                    "Candidate={} | Distance={}",
                    metadatas[i].get("candidate_name"),
                    distances[i],
                )

            for i in range(len(documents)):

                distance = distances[i]

                #
                # Keep only sufficiently similar chunks.
                #

                
                if distance > distance_threshold:
                    continue

                metadata = metadatas[i] if metadatas else {}

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
                    }
                )

            #
            # Ensure closest chunks appear first.
            #
            normalized_results.sort(
                key=lambda x: x["distance"]
            )

            return normalized_results

        except Exception as e:

            print(
                f"Error retrieving resume chunks using similarity threshold: {e}"
            )
            return None

        finally:

            if client:
                client.clear_system_cache()
                del client

            if collection:
                del collection

            gc.collect()

    
    def derive_resume_chunks_cosine_similarity_threshold(
        self,
        session_id: str,
        query_embedding: list[float],
        cosine_similarity_threshold: float = 0.75,
        max_results: int = 300,
    ):
        """
        Retrieve resume chunks whose cosine similarity is greater than or
        equal to the specified threshold.

        ChromaDB internally returns cosine distance:

            cosine_distance = 1 - cosine_similarity

        Since ChromaDB does not support similarity threshold filtering during
        query, we retrieve a large number of nearest neighbours and filter
        them afterwards.

        Returns chunks sorted by decreasing cosine similarity.
        """

        client = None
        collection = None
        logger = get_logger()

        try:

            #
            # Convert cosine similarity threshold to Chroma distance threshold.
            #
            distance_threshold = 1 - cosine_similarity_threshold

            client, collection = self._get_collection(session_id)

            logger.info(
                "Collection metadata: {}",
                collection.metadata,
            )

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
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

                distance = distances[i]
                cosine_similarity = 1 - distance

                logger.info(
                    "Candidate={} | document={} | Cosine Similarity={:.4f}",
                    metadatas[i].get("candidate_name"),
                    documents[i][:500],
                    cosine_similarity,
                )

                #
                # Keep only sufficiently similar chunks.
                #
                if distance > distance_threshold:
                    continue

                metadata = metadatas[i] if metadatas else {}

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
                        "distance": distance,  # kept for debugging
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

            logger.info(
                "Retrieved {} chunk(s) with cosine similarity >= {:.2f}",
                len(normalized_results),
                cosine_similarity_threshold,
            )

            return normalized_results

        except Exception as e:

            logger.exception(
                "Error retrieving resume chunks using cosine similarity threshold | error={}",
                e,
            )

            return None

        finally:

            if client:
                client.clear_system_cache()
                del client

            if collection:
                del collection

            gc.collect()

    


    def derive_resume_chunks_dynamic_similarity_threshold(
        self,
        session_id: str,
        query_embedding: list[float],
        minimum_cosine_similarity: float = 0.20,
        similarity_delta: float = 0.05,
        max_results: int = 300,
    ):
        """
        Retrieve resume chunks using a dynamic cosine similarity threshold.

        ChromaDB internally returns cosine distance:

            cosine_distance = 1 - cosine_similarity

        Workflow:
        1. Retrieve top max_results nearest neighbours.
        2. Compute the highest cosine similarity.
        3. Compute a dynamic threshold:
                max(
                    minimum_cosine_similarity,
                    best_similarity - similarity_delta
                )
        4. Keep only chunks above the dynamic threshold.

        Returns chunks sorted by decreasing cosine similarity.
        """

        client = None
        collection = None
        logger = get_logger()

        try:

            client, collection = self._get_collection(session_id)

            logger.info(
                "Collection metadata: {}",
                collection.metadata,
            )

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            embeddings = (
                results.get("embeddings", [[]])[0]
                if results.get("embeddings")
                else []
            )
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]

            #
            # Build all retrieved chunks first.
            #
            all_results = []

            for i in range(len(documents)):

                distance = distances[i]
                cosine_similarity = 1 - distance

                metadata = metadatas[i] if metadatas else {}

                logger.info(
                    "Candidate={} | Cosine Similarity={:.4f}",
                    metadata.get("candidate_name"),
                    cosine_similarity,
                )

                all_results.append(
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

            if not all_results:

                logger.info(
                    "No chunks retrieved from Chroma."
                )

                return []

            #
            # Determine dynamic similarity threshold.
            #
            best_similarity = max(
                row["cosine_similarity"]
                for row in all_results
            )

            dynamic_threshold = max(
                minimum_cosine_similarity,
                best_similarity*0.9,
            )

            logger.info(
                "Best Cosine Similarity={:.4f} | Dynamic Threshold={:.4f}",
                best_similarity,
                dynamic_threshold,
            )

            normalized_results = []

            for row in all_results:

                if row["cosine_similarity"] < dynamic_threshold:
                    continue

                logger.info(
                    "Keeping chunk | Candidate={} | Similarity={:.4f}",
                    row["candidate_name"],
                    row["cosine_similarity"],
                )

                normalized_results.append(row)

            #
            # Highest similarity first.
            #
            normalized_results.sort(
                key=lambda x: x["cosine_similarity"],
                reverse=True,
            )

            logger.info(
                "Retrieved {} chunk(s) after dynamic filtering.",
                len(normalized_results),
            )

            return normalized_results

        except Exception as e:

            logger.exception(
                "Error retrieving resume chunks using dynamic cosine similarity threshold | error={}",
                e,
            )

            return None

        finally:

            if client:
                client.clear_system_cache()
                del client

            if collection:
                del collection

            gc.collect()