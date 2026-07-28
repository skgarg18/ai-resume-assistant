from utils.log_utils import bind_logger
from time import perf_counter



from services.vector_db_store import chroma_client
from services.email_service import send_completion_email, send_failure_email

from database.active_repository import (
    session_repo,
    resume_repo, 
    resume_chunks_repo, 
    files_repo,
)

from pathlib import Path

from config.constants import FRONTEND_URL
from chromadb.errors import NotFoundError


from utils.extracting_from_files import extract_top_from_files

from utils.evaluate_resume import evaluate_resume


def process_resumes_job(
        session_id: str,
        jd: str,
        files_data: list[dict],
        notificationEmail: str
    ):

    logger = bind_logger(session_id=session_id)

    logger.info("worker started")

    start = perf_counter()

    # two variables to store rows to be inserted in db
    chunk_rows = []
    resume_data_rows = []

    succesful = 0
    failed = 0

    try:
        

        # Extracting top 10 resumes

        logger.info(
            "Starting resume text extraction and initial ranking",
        )

        result = extract_top_from_files(
            session_id=session_id,
            files_data=files_data,
            jd=jd
        )


        search_results = result["search_results"]
        resume_data = result["resume_data"]

        logger.info(
            "Top resumes extracted | shortlisted={}",
            len(search_results["ids"][0]),
        )


        # -----------------------------------------------------------------------
        # Evaluating shortisted resumes and storing required results in db
        # ------------------------------------------------------------------------

        evaluation_start = perf_counter()

        # Use Groq LLM to evaluate the shortlisted resumes

        logger.info(
            "Starting evaluation of {} shortlisted resumes",
            len(search_results['ids'][0])
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

                succesful += 1
            
            except Exception :

                logger.exception(
                    "Failed to process resume | filename={}",
                    filename,
                )

                failed += 1

                try:
                    extension = Path(filename).suffix.lower()
                    file_path = f"{session_id}/{res_id}{extension}"
                    files_repo.delete_file(file_path)

                except Exception:
                    logger.exception(
                        "Failed to cleanup file | {}",
                        filename,
                    )



        logger.info(
            "Resume evaluation completed | resumes={} | duration={:.2f}s",
            len(resume_data_rows),
            perf_counter() - evaluation_start,
        )


       # After all looping done, storing results

        if not resume_data_rows:

            send_fail = send_failure_email(
                to_email=notificationEmail,
                succesful=succesful,
                failed=failed
            )

            if not send_fail:
                logger.warning("Failure email could not be sent")

                session = session_repo.update_session_details(
                    session_id=session_id,
                    status="failed",
                    successful_resumes=succesful,
                    failed_resumes=failed,
                    email_status="failed"
                )

                if session is None:
                    raise Exception("Failed to update session")
            
            else:
                session = session_repo.update_session_details(
                    session_id=session_id,
                    status="failed",
                    successful_resumes=succesful,
                    failed_resumes=failed,
                    email_status="sent"
                )

                if session is None:
                    raise Exception("Failed to update session")

            return {
            "session_id": session_id,
            "processed": len(resume_data_rows),
            "status": "failed",
            }
            

          
        
        logger.info(
            "Saving {} resumes to database",
            len(resume_data_rows)
        )

        response = resume_repo.add_resume_data(resume_data_rows)

        if response is None:
            raise Exception("Failed to add resume data to the database.")


        if chunk_rows:
        
            logger.info(
                "Saving {} resume chunks",
                len(chunk_rows)
            )

            response = resume_chunks_repo.add_resume_chunks(chunk_rows)
            if response is None:
                raise Exception("Failed to add chunk data to the database.")


        logger.info(
            "Deleting temporary Chroma collection "
        )

        # Deleting collection because no longer needed
        chroma_client.delete_collection(
            name=f"session_{session_id}"
        )


        logger.info(
            "Resume evaluation completed  | successful={} | failed={} | duration={:.2f}s",
            succesful,
            failed,
            perf_counter() - start,
        )

        link = f"{FRONTEND_URL}/session/{session_id}"

       
        send_comp = send_completion_email(
            to_email=notificationEmail,
            succesful=succesful,
            failed=failed,
            link=link
        )

        if not send_comp:
            logger.warning("Completion email could not be sent")

            session = session_repo.update_session_details(
                session_id=session_id,
                status="completed",
                successful_resumes=succesful,
                failed_resumes=failed,
                email_status="failed"
            )

            if session is None:
                raise Exception("Failed to update session")
        

        else:
            session = session_repo.update_session_details(
                session_id=session_id,
                status="completed",
                successful_resumes=succesful,
                failed_resumes=failed,
                email_status="success"
            )

            if session is None:
                    raise Exception("Failed to update session")
        

        return {
            "session_id": session_id,
            "processed": len(resume_data_rows),
            "status": "completed",
        }
    
    except Exception as e:

        logger.exception(
            "Upload session failed"
        )

        # Deleting the croma collection
        try:
            chroma_client.delete_collection(
                name=f"session_{session_id}"
            )
        
        except NotFoundError:
            logger.info(
                "Chroma collection already deleted or not found"
            )
            
        except Exception:
            logger.exception(
                "Failed to delete chroma client"
            )

        send_fail = send_failure_email(
            to_email=notificationEmail,
            succesful=succesful,
            failed=failed
        )

        if not send_fail:
            logger.warning("Failure email could not be sent")

            session = session_repo.update_session_details(
                session_id=session_id,
                status="failed",
                successful_resumes=succesful,
                failed_resumes=failed,
                email_status="failed"
            )

            if session is None:
                logger.error(
                    "Failed to update session status"
                )
        
        else:
            session = session_repo.update_session_details(
                session_id=session_id,
                status="failed",
                successful_resumes=succesful,
                failed_resumes=failed,
                email_status="success",
                reason=e
            )

            if session is None:
                logger.error(
                    "Failed to update session status"
                )
        
        raise
        
