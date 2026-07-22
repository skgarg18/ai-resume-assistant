from services.vector_db_store import chroma_client
from utils.text_extraction_util import extract_text_from_file
from services.embedding_model import get_embedding_model

import uuid


def extract_top_from_files(
    session_id: str,
    files_data: list,
    jd: str
):
    
    embedding_model = get_embedding_model()

    # Embed JD
    jd_embedding = embedding_model.encode(
        jd
    ).tolist()


    collection = chroma_client.get_or_create_collection(
        name=f"session_{session_id}"
    )

    resume_data = {}




    # Parse resumes
    for file in files_data:

        resume_id = str(uuid.uuid4())

    
        content = file["content"]
    
        filename = file["filename"]
    
        text = extract_text_from_file(content , filename)

        # Keep PDF and text in memory for now
        resume_data[resume_id] = {
            "content": content,
            "text": text,
            "filename": filename
        }
    
    
        embedding = embedding_model.encode(text).tolist()


        collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[
                {
                    "filename": filename,
                    "type": "resume"
                }
            ],
            ids=[resume_id]
        )


    search_results = collection.query(
        query_embeddings=[jd_embedding],
        n_results=min(
            10,
            len(files_data)
        )
    )


    return {
        "search_results": search_results,
        "resume_data": resume_data
    }