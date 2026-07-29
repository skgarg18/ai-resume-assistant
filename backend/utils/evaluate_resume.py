from utils.log_utils import get_logger
from time import perf_counter


from pathlib import Path

from database.active_repository import files_repo

from langchain_chains.evaluation_chain import evaluation_chain
from langchain_chains.metadata_chain2 import process_resume
from schema.resume_analysis import ResumeEvaluation

from utils.extract_candidate_details import extract_details

from services.text_splitter import splitter
from services.embedding_model import get_embedding_model

from utils.llm_usage_log_utils import log_llm_usage

def evaluate_resume(
    res_id,
    res_text,
    filename,
    session_id,
    resume_data,
    jd,
):
    
    logger = get_logger().bind(filename=filename)
    
    start = perf_counter()
    
    logger.info(
        "Starting resume data extraction , evaluation , chunking"
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

        metadata_response = process_resume(res_text , session_id , filename)

        metadata_response = metadata_response.model_dump()

        logger.info(
            "Metadata extracted | duration={:.2f}s",
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
            "Starting resume evaluation | candidate={}",
            candidate_details["name"]
        )

        logger.info(
            "Resume length | candidate={} | chars={}",
            candidate_details["name"],
            len(res_text),
        )

        logger.info("JD length | chars={}", len(jd))
        
        # ADD RETRY LOOP AND FALLBACK LOGIC HERE:
        max_retries = 3
        evaluation_response = None
        eval_parsed = None

        for attempt in range(max_retries):
            try:
                evaluation_response = evaluation_chain.invoke(
                    {
                        "jd": jd,
                        "resume": res_text,
                    }
                )
                
                eval_parsed = evaluation_response.get("parsed")
                
                # Manual Fallback Parsing (if LangChain failed to auto-parse tool call)
                if not eval_parsed and evaluation_response.get("raw"):
                    raw_msg = evaluation_response["raw"]
                    if hasattr(raw_msg, "tool_calls") and raw_msg.tool_calls:
                        logger.info("Evaluation LangChain auto-parse failed. Attempting fallback tool call extraction.")
                        try:
                            eval_parsed = ResumeEvaluation(**raw_msg.tool_calls[0]["args"])
                        except Exception as parse_err:
                            logger.error("Fallback evaluation parsing failed: {}", parse_err)

                if eval_parsed:
                    log_llm_usage(
                        operation="Resume evaluation against JD",
                        response=evaluation_response["raw"],
                        latency_ms=(perf_counter() - evaluation_start) * 1000,
                        session_id=session_id,
                        success=True,
                    )
                    break  # Evaluation succeeded!
                else:
                    logger.warning("Evaluation attempt {} failed to parse. Retrying...", attempt + 1)

            except Exception as e:
                logger.warning("Evaluation API call failed on attempt {}: {}. Retrying...", attempt + 1, str(e))
                if attempt == max_retries - 1:
                    log_llm_usage(
                        operation="Resume evaluation against JD",
                        response=None,
                        latency_ms=(perf_counter() - evaluation_start) * 1000,
                        session_id=session_id,
                        success=False,
                        error=str(e),
                    )
                    raise e

        if not eval_parsed:
            raise ValueError("Resume evaluation failed after maximum retry attempts.")

        # Convert parsed object to dictionary
        evaluation = eval_parsed.model_dump()

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
            "score": evaluation["score_breakdown"],
            "overall_score" : match_score,
            "summary": evaluation["summary"],
            "matched_skills": evaluation["top_matched_skills"],
            "missing_skills": evaluation["missing_skills"],
            "file_url": file_path,
            "recruiter_insights": metadata_response["recruiter_insights"],
            **metadata_response,
        }


        # -------------------------
        # Chunking & Embeddings
        # -------------------------

        chunk_start = perf_counter()

        chunks = splitter.split_text(res_text)

        chunk_embeddings = embedding_model.encode(
            chunks,
            normalize_embeddings=True,
            ).tolist()

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
            "Chunking and embeddings completed | chunks={} | duration={:.2f}s",
            len(chunks),
            perf_counter() - chunk_start,
        )

        # -------------------------
        # Upload resume
        # -------------------------

        response = files_repo.store_file(file_path, file_content)

        if not response:
            logger.error(
                "Failed to upload resume file"
            ) 
            raise Exception("File upload returned False.")
        
        logger.info(
            "Resume uploaded"
        )



        logger.info(
            "Extraction/Evaluation/Chunking Complete | duration = {:.2f}s",
            perf_counter() - start,
        )

        return {
            "resume_data": resume_data_row,
            "chunk_rows": chunk_rows
        }

    except Exception as e :
        logger.exception(
            "Resume processing failed | error={}" , e,
        )
        
        raise 