from time import perf_counter
from utils.log_utils import bind_logger

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional


from services.llm_initialization import groq_client

from database.active_repository import (
    session_repo ,
    google_user_repo
)


from prompts.session_name_prompt import get_prompt_session_name


from utils.extract_from_drive import extract_files_from_drive

from utils.llm_usage_log_utils  import log_groq_usage

from typing import List

import uuid

from rq_queue.redis_connection import resume_queue

from jobs.resume_job import process_resumes_job

from auth.dependencies import get_current_user

router = APIRouter()

@router.post("/api/upload")
async def upload_and_screen(
    jd: str = Form(...),
    drive_link: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    notificationEmail: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    current_user=Depends(get_current_user),
):  
    
    # Creating a session id 
    session_id = str(uuid.uuid4())

    logger = bind_logger(session_id=session_id)

    start = perf_counter()

    logger.info(
        "Resume upload request received | drive_link={} | uploaded_files={} | email={}",
        bool(drive_link),
        len(files) if files else 0,
        notificationEmail
    )


    logger.info("Created upload session")

    try:

    # ----------------------------------------------------------------------------------------------------
    #  Session creation, and storing in db , Jd embedding, chroma db collection storage
    # -----------------------------------------------------------------------------------------------------
 
        #Creating a session_name

        logger.info(
            "Generating session title"
        )

        jd_prompt = get_prompt_session_name(jd)

        jd_start = perf_counter()

        jd_start = perf_counter()

        try:
            title_response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": jd_prompt}],
                model="llama-3.1-8b-instant", # Groq supports Llama 3!
            )

            session_name = title_response.choices[0].message.content.strip()

            log_groq_usage(
                operation="session_name_extraction",
                response=title_response,
                latency_ms=(perf_counter() - jd_start) * 1000,
                session_id=session_id,
                success=True,
            )

        except Exception as e:
            log_groq_usage(
                operation="session_name_extraction",
                response=None,
                latency_ms=(perf_counter() - jd_start) * 1000,
                session_id=session_id,
                success=False,
                error=str(e),
            )
            raise

        
        logger.info(
            "Session title generated {}",
            session_name,
        )


        # --------------------------------------------------------------
        # Converting files into dictionary format
        # --------------------------------------------------------------

        files_data = []

        if drive_link:

            logger.info(
                "Extracting resumes from Google Drive",
            )

            logger.info(
                "Extracting user data for user={}",
                user_id
            )

            user_data = google_user_repo.get_user_data_by_user_id(user_id)

            if user_data is None:

                logger.error(
                    "error fetching user data for user_id={}",
                    user_id
                )

                raise HTTPException(
                    status_code=404,
                    detail=f"Error fetching data for user = {user_id}"
                )
            
            logger.info(
                "user data fetched succesfully"
            )
            

            
            files_data = extract_files_from_drive(drive_link , user_data)

            logger.info(
                "Retrieved {} files from Drive",
                len(files_data),
            )

            notificationEmail = user_data.email


        if files:
            
            for file in files:
                files_data.append(
                    {
                        "filename": file.filename,
                        "content": await file.read()
                    }
                )
            
            logger.info(
                "Received {} uploaded PDF files",
                len(files_data),
            )
        

        job_id = str(uuid.uuid4())

        session = session_repo.add_session_details(
            session_id=session_id,
            user_id=current_user["sub"],
            session_name=session_name,
            jd_description=jd,
            upload_source = "drive" if drive_link else "files",
            total_resumes=len(files_data),
            rq_job_id=job_id,
            user_email=notificationEmail
        )

        logger.info(
            "Session stored in database",
        )

        if not session:

            logger.error(
                "Failed to create session in database",
            )

            raise HTTPException(
                status_code = 500,
                detail = "Error adding session details"
            )

        try:
            job = resume_queue.enqueue(
                process_resumes_job,
                session_id,
                jd,
                files_data,
                notificationEmail,
                job_id=job_id,
                job_timeout="2h",
            )

        except Exception as e:
            logger.exception(
                "Failed to enqueue RQ job id {}",
                job_id,
            )

            session_repo.update_session_details(
                session_id=session_id,
                status="failed",
                reason=e
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to queue resume processing."
            )

        logger.info(
            "Resume processing job queued | job_id={} | duration={:.2f}s",
            job.id,
            perf_counter() - start,
        )

                

         
        # Return the current session_id
        return {
            "session_id": session_id,
            "job_id": job_id,
            "status": "queued"
        }


    except Exception as e:

        logger.exception(
            "Upload session failed"
        )


        # Deleting if any sessions data uploaded in db
        try:
            session_repo.delete_session_by_id(session_id)
        except Exception:
            logger.exception(
                "Failed to delete session | session_id=%s",
                session_id,
            )
        
        # Raising exception
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


