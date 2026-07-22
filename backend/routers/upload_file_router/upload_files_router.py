import logging
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional


from pathlib import Path

from services.vector_db_store import chroma_client
from services.llm_initialization import groq_client

from database.active_repository import (
    session_repo ,
)


from prompts.session_name_prompt import get_prompt_session_name


from routers.upload_file_router.extractions.extract_from_drive import extract_files_from_drive

from logs.llm_usage import log_groq_usage

from typing import List

import uuid

from rq_queue.redis_connection import resume_queue

from jobs.resume_job import process_resumes_job
router = APIRouter()

@router.post("/api/upload")
async def upload_and_screen(
    jd: str = Form(...),
    drive_link: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    start = perf_counter()

    logger.info(
        "Resume upload request received | drive_link=%s | uploaded_files=%d",
        bool(drive_link),
        len(files) if files else 0,
    )


    # Creating a session id 
    session_id = str(uuid.uuid4())

    logger.info("Created upload session | session_id=%s", session_id)

    try:

    # ----------------------------------------------------------------------------------------------------
    #  Session creation, and storing in db , Jd embedding, chroma db collection storage
    # -----------------------------------------------------------------------------------------------------
 
        #Creating a session_name

        logger.info(
            "Generating session title | session_id=%s",
            session_id
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
            "Session title generated | session_id=%s | title=%s",
            session_id,
            session_name,
        )


        # --------------------------------------------------------------
        # Converting files into dictionary format
        # --------------------------------------------------------------

        files_data = []

        if drive_link:

            logger.info(
                "Extracting resumes from Google Drive | session_id=%s",
                session_id
            )
            
            files_data = extract_files_from_drive(drive_link)

            logger.info(
                "Retrieved %d files from Drive | session_id=%s",
                len(files_data),
                session_id,
            )


        if files:
            
            for file in files:
                files_data.append(
                    {
                        "filename": file.filename,
                        "content": await file.read()
                    }
                )
            
            logger.info(
                "Received %d uploaded PDF files | session_id=%s",
                len(files_data),
                session_id,
            )
        

        

        job = resume_queue.enqueue(
            process_resumes_job,
            session_id,
            jd,
            files_data,
            job_timeout="2h"
        )

        logger.info(
            "Resume processing job queued | session_id=%s | job_id=%s | duration=%2fs",
            session_id,
            job.id,
            perf_counter() - start,
        )

                # Storing jd and session_id

        session = session_repo.add_session_details(
            session_id=session_id,
            session_name=session_name,
            jd_description=jd,
            upload_source = "drive" if drive_link else "files",
            total_resumes=len(files_data),
            rq_job_id=job.id,
        )

        logger.info(
            "Session stored in database | session_id=%s",
            session_id
        )

        if not session:

            logger.error(
                "Failed to create session in database | session_id=%s",
                session_id,
            )

            raise HTTPException(
                status_code = 500,
                detail = "Error adding session details"
            )

         
        # Return the current session_id
        return {
            "session_id": session_id,
            "job_id": job.id,
            "status": "queued"
        }


    except Exception as e:

        logger.exception(
            "Upload session failed | session_id=%s",
            session_id,
        )


        # Deleting if any sessions data uploaded in db
        try:
            session_repo.delete_session_by_id(session_id)
        except Exception:
            logger.exception(
                "Failed to delete session | session_id=%s",
                session_id,
            )
        
            
        except Exception:
            logger.exception(
                "Failed to delete chroma client | session_id=%s",
                session_id,
            )
        
        # Raising exception
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


