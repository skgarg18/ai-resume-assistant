import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from pathlib import Path

from database.active_repository import files_repo

from routers.upload_file_router.chains.evaluation_chain import evaluation_chain
from routers.upload_file_router.chains.metadata_extraction_chain import metadata_chain
from routers.upload_file_router.chains.metadata_chain2 import process_resume

from resume_generator.generator import build_format_resume

from utils.extract_candidate_details import extract_details

from services.text_splitter import splitter
from services.embedding_model import get_embedding_model

from logs.llm_usage import log_llm_usage

def evaluate_resume(
    res_id,
    res_text,
    filename,
    session_id,
    resume_data,
    jd,
):
    
    start = perf_counter()
    
    logger.info(
        "Starting resume data extraction , evaluation , chunking | session_id=%s | filename=%s",
        session_id,
        filename,
    )
    

    embedding_model = get_embedding_model()

    try:
        extension = Path(filename).suffix.lower()

        file_content = resume_data[res_id]["content"]
        file_path = f"{session_id}/{res_id}{extension}"

            
        # -------------------------
        # Metadata Extraction
        # -------------------------

        metadata_start = perf_counter()

        metadata_response = process_resume(res_text , session_id)

        metadata_response = metadata_response.model_dump()

        metadata_row = {
            "resume_id": str(res_id),
            "session_id": session_id,
            **metadata_response,
        }

        logger.info(
            "Metadata extracted |session_id=%s| filename=%s | duration=%.2fs",
            session_id,
            filename,
            perf_counter() - metadata_start,
        )


        candidate_details = extract_details(
            metadata_response["basic_info"]
        )


        # -------------------------
        # Resume Evaluation
        # -------------------------

        evaluation_start = perf_counter()

        logger.info(
            "Starting resume evaluation | session_id=%s | candidate=%s | filename=%s",
            session_id,
            candidate_details["name"],
            filename,
        )

        try:
            logger.info(
                "Resume length | candidate=%s | chars=%d",
                candidate_details["name"],
                len(res_text),
            )

            logger.info("JD length | chars=%d", len(jd))
            
            evaluation = evaluation_chain.invoke(
                {
                    "jd": jd,
                    "resume": res_text,
                }
            )

            log_llm_usage(
                operation="Resume evaluation against JD",
                response=evaluation["raw"],
                latency_ms=(perf_counter() - evaluation_start) * 1000,
                session_id=session_id,
                success=True,
            )

        except Exception as e:
            log_llm_usage(
                operation="Resume evaluation against JD",
                response=None,
                latency_ms=(perf_counter() - evaluation_start) * 1000,
                session_id=session_id,
                success=False,
                error=str(e),
            )
            raise
            
        evaluation = evaluation["parsed"].model_dump()

        # Remove duplicate skills
        evaluation["top_matched_skills"] = list(
            dict.fromkeys(evaluation["top_matched_skills"])
        )

        evaluation["missing_skills"] = list(
            dict.fromkeys(evaluation["missing_skills"])
        )

        breakdown = evaluation["score_breakdown"]

        match_score = round(
            breakdown["technical_skills"] * 0.35
            + breakdown["professional_experience"] * 0.25
            + breakdown["project_evidence"] * 0.20
            + breakdown["education_and_training"] * 0.10
            + breakdown["domain_relevance"] * 0.10
        )

        resume_data_row = {
            "resume_id": str(res_id),
            "session_id": session_id,
            "name": candidate_details["name"],
            "email": candidate_details["email"],
            "contact": candidate_details["phone"],
            "score": match_score,
            "summary": evaluation["summary"],
            "matched_skills": evaluation["top_matched_skills"],
            "missing_skills": evaluation["missing_skills"],
            "file_url": file_path,
            "recruiter_insights": metadata_response["recruiter_insights"],
        }


        # -------------------------
        # Chunking & Embeddings
        # -------------------------

        chunk_start = perf_counter()

        chunks = splitter.split_text(res_text)

        chunk_embeddings = embedding_model.encode(chunks).tolist()

        chunk_rows = []

        for idx, (chunk, chunk_embedding) in enumerate(
            zip(chunks, chunk_embeddings)
        ):
            chunk_rows.append(
                {
                    "session_id": session_id,
                    "resume_id": res_id,
                    "chunk_text": chunk,
                    "embedding": chunk_embedding,
                    "candidate_name": candidate_details["name"],
                    "chunk_index": idx,
                }
            )

        logger.info(
            "Chunking and embeddings completed | session_id=%s | filename=%s | chunks=%d | duration=%.2fs",
            session_id,
            filename,
            len(chunks),
            perf_counter() - chunk_start,
        )

        # -------------------------
        # Upload resume
        # -------------------------

        response = files_repo.store_file(file_path, file_content)

        if not response:
            logger.error(
                "Failed to upload resume file | session_id=%s | filename=%s",
                session_id,
                filename,
            ) 
            raise Exception("File upload returned False.")
        
        logger.info(
            "Resume uploaded | session_id=%s | filename=%s",
            session_id,
            filename
        )



        logger.info(
            "Extraction/Evaluation/Chunking Complete | session_id=%s | filename = %s | duration = %2fs",
            session_id,
            filename,
            perf_counter() - start,
        )

        return {
            "resume_data": resume_data_row,
            "resume_metadata": metadata_row,
            "chunk_rows": chunk_rows,
        }

    except Exception:
        logger.exception(
            "Resume processing failed | session_id=%s | filename=%s",
            session_id,
            filename,
        )
        
        raise 