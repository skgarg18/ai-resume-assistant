import logging
from time import perf_counter

logger = logging.getLogger(__name__)


from services.vector_db_store import chroma_client
from services.email_service import send_completion_email, send_failure_email

from database.active_repository import (
    session_repo,
    resume_repo, 
    resume_chunks_repo, 
    files_repo,
    resume_metadata_repo
)

from pathlib import Path

from chromadb.errors import NotFoundError


from routers.upload_file_router.extractions.extracting_from_files import extract_top_from_files
from routers.upload_file_router.extractions.extract_from_drive import extract_files_from_drive

from routers.upload_file_router.evaluate_resume import evaluate_resume


def process_resumes_job(
        session_id: str,
        jd: str,
        files_data: list[dict],
    ):

    start = perf_counter()

    # two variables to store rows to be inserted in db
    chunk_rows = []
    resume_data_rows = []
    metadata_rows = []

    succesful = 0
    failed = 0

    try:
        

        # Extracting top 10 resumes

        logger.info(
            "Starting resume text extraction and initial ranking | session_id=%s",
            session_id,
        )

        result = extract_top_from_files(
            session_id=session_id,
            files_data=files_data,
            jd=jd
        )


        search_results = result["search_results"]
        resume_data = result["resume_data"]

        logger.info(
            "Top resumes extracted | session_id=%s | shortlisted=%d",
            session_id,
            len(search_results["ids"][0]),
        )


        # -----------------------------------------------------------------------
        # Evaluating shortisted resumes and storing required results in db
        # ------------------------------------------------------------------------

        evaluation_start = perf_counter()

        # Use Groq LLM to evaluate the shortlisted resumes

        logger.info(
            "Starting evaluation of %d shortlisted resumes | session_id=%s",
            len(search_results['ids'][0]),
            session_id,
        )


        for i in range(len(search_results['ids'][0])):
        
            res_id = search_results['ids'][0][i]
            res_text = search_results['documents'][0][i]
            filename = search_results['metadatas'][0][i]['filename']

            try:

                response = evaluate_resume(
                    res_id,
                    res_text,
                    filename, 
                    session_id , 
                    resume_data , 
                    jd)

                resume_data_rows.append(response["resume_data"])
                chunk_rows.extend(response["chunk_rows"])
                metadata_rows.append(response["resume_metadata"])

                succesful += 1
            
            except Exception :

                logger.exception(
                    "Failed to process resume | session_id=%s | filename=%s",
                    session_id,
                    filename,
                )

                failed += 1

                try:
                    extension = Path(filename).suffix.lower()
                    file_path = f"{session_id}/{res_id}{extension}"
                    files_repo.delete_file(file_path)

                except Exception:
                    logger.exception(
                        "Failed to cleanup file | %s",
                        filename,
                    )



        logger.info(
            "Resume evaluation completed | session_id=%s | resumes=%d | duration=%.2fs",
            session_id,
            len(resume_data_rows),
            perf_counter() - evaluation_start,
        )


       # After all looping done, storing results

        if not resume_data_rows:

            session = session_repo.update_session_details(
                session_id=session_id,
                status="failed",
                successful_resumes=0,
                failed_resumes=failed,
            )

            if session is None:
                raise Exception("Failed to update session")



            send_fail = send_failure_email(
                to_email="shubham.k.garg@globallogic.com",
                succesful=succesful,
                failed=failed,
                session_id=session_id
            )

            if not send_fail:
                logger.warning("Failure email could not be sent")



            return {
            "session_id": session_id,
            "processed": len(resume_data_rows),
            "status": "failed",
            }
            

          
        
        logger.info(
            "Saving %d resumes to database | session_id=%s",
            len(resume_data_rows),
            session_id,
        )

        response = resume_repo.add_resume_data(resume_data_rows)

        if response is None:
            raise Exception("Failed to add resume data to the database.")


        if chunk_rows:
        
            logger.info(
                "Saving %d resume chunks | session_id=%s",
                len(chunk_rows),
                session_id
            )

            response = resume_chunks_repo.add_resume_chunks(chunk_rows)
            if response is None:
                raise Exception("Failed to add chunk data to the database.")


        if metadata_rows:
        
            logger.info(
                "Saving %d metadata records | session_id=%s",
                len(metadata_rows),
                session_id
            )

            response = resume_metadata_repo.add_resume_metadata(metadata_rows)
            if response is None:
                raise Exception("Failed to add metadata to the database.")


        logger.info(
            "Deleting temporary Chroma collection | session_id=%s",
            session_id,
        )

        # Deleting collection because no longer needed
        chroma_client.delete_collection(
            name=f"session_{session_id}"
        )


        session = session_repo.update_session_details(
            session_id=session_id,
            status="completed",
            successful_resumes=succesful,
            failed_resumes=failed,
        )

        if session is None:
            raise Exception("Failed to update session")


        logger.info(
            "Resume evaluation completed | session_id=%s | successful=%d | failed=%d | duration=%.2fs",
            session_id,
            succesful,
            failed,
            perf_counter() - start,
        )

        link = f"http://localhost:3000/session/{session_id}"

       
        send_comp = send_completion_email(
            to_email="shubham.k.garg@globallogic.com",
            succesful=succesful,
            failed=failed,
            link=link,
            session_id=session_id
        )

        if not send_comp:
            logger.warning("Completion email could not be sent")
        

        return {
            "session_id": session_id,
            "processed": len(resume_data_rows),
            "status": "completed",
        }
    
    except Exception as e:

        logger.exception(
            "Upload session failed | session_id=%s",
            session_id,
        )

        session = session_repo.update_session_details(
            session_id=session_id,
            status="failed",
            successful_resumes=succesful,
            failed_resumes=failed,
        )

        if session is None:
            logger.error(
                "Failed to update session status | session_id=%s",
                session_id,
            )

        # Deleting the croma collection
        try:
            chroma_client.delete_collection(
                name=f"session_{session_id}"
            )
        
        except NotFoundError:
            logger.info(
                "Chroma collection already deleted or not found | session_id=%s",
                session_id,
            )
            
        except Exception:
            logger.exception(
                "Failed to delete chroma client | session_id=%s",
                session_id,
            )




        send_fail = send_failure_email(
            to_email="shubham.k.garg@globallogic.com",
            succesful=succesful,
            failed=failed,
            session_id=session_id
        )

        if not send_comp:
            logger.warning("Failure email could not be sent")



        
        raise
        
