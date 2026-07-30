from time import perf_counter
import uuid

# Replace 'get_embedding_model' with wrapper functions
from services.embedding_model import encode_query, encode_documents
from services.vector_db_store import chroma_client
from utils.log_utils import get_logger
from utils.text_extraction_util import extract_text_from_file


def extract_top_from_files(
    session_id: str,
    files_data: list,
    jd: str,
):
    """
    Extract text from uploaded resumes, generate embeddings,
    store them in ChromaDB and return the top matching resumes.
    """

    logger = get_logger()

    logger.info(
        "Starting resume extraction and embedding generation | total_files={}",
        len(files_data),
    )

    start = perf_counter()

    logger.info("Generating embedding for job description")

    # ----------------------------------------------------------
    # 1. Generate JD embedding (JD acts as the Query)
    # ----------------------------------------------------------
    jd_embedding = encode_query(jd)

    # ----------------------------------------------------------
    # 2. Create temporary Chroma collection
    # ----------------------------------------------------------

    logger.info(
        "Creating temporary Chroma collection | collection=session_{}",
        session_id,
    )

    collection = chroma_client.get_or_create_collection(
        name=f"session_{session_id}"
    )

    resume_data = {}

    # ----------------------------------------------------------
    # 3. Process & Index Resumes
    # ----------------------------------------------------------

    for index, file in enumerate(files_data, start=1):

        resume_start = perf_counter()

        resume_id = str(uuid.uuid4())

        content = file["content"]
        filename = file["filename"]

        logger.info(
            "Processing resume {}/{} | filename={}",
            index,
            len(files_data),
            filename,
        )

        text = extract_text_from_file(
            content,
            filename,
        )

        # Keep original file and extracted text in memory
        resume_data[resume_id] = {
            "content": content,
            "text": text,
            "filename": filename,
        }

        # Resume text acts as the Document
        embedding = encode_documents([text])[0]

        collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[
                {
                    "filename": filename,
                    "type": "resume",
                }
            ],
            ids=[resume_id],
        )

        logger.info(
            "Resume indexed successfully | filename={} | duration={:.2f}s",
            filename,
            perf_counter() - resume_start,
        )

    # ----------------------------------------------------------
    # 4. Retrieve Top Matching Resumes
    # ----------------------------------------------------------

    logger.info(
        "Searching for top {} matching resumes",
        min(10, len(files_data)),
    )

    search_results = collection.query(
        query_embeddings=[jd_embedding],
        n_results=min(
            10,
            len(files_data),
        ),
    )

    logger.info(
        "Resume extraction completed | shortlisted={} | duration={:.2f}s",
        len(search_results["ids"][0]),
        perf_counter() - start,
    )

    return {
        "search_results": search_results,
        "resume_data": resume_data,
    }