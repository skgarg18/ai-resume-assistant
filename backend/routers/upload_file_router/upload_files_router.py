from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from pathlib import Path

from services.text_splitter import splitter
from services.vector_db_store import chroma_client
from services.embedding_model import get_embedding_model
from services.llm_initialization import groq_client

from database.active_repository import (
    session_repo ,
    resume_repo, 
    resume_chunks_repo, 
    files_repo
)


from utils.extract_candidate_details import extract_details

from prompts.session_name_prompt import get_prompt_session_name

from routers.upload_file_router.chains.evaluation_chain import evaluation_chain

from routers.upload_file_router.extractions.extracting_from_files import extract_top_from_files
from routers.upload_file_router.extractions.extract_from_drive import extract_files_from_drive

from typing import List

import uuid

router = APIRouter()

@router.post("/api/upload")
async def upload_and_screen(
    jd: str = Form(...),
    drive_link: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    
    embedding_model = get_embedding_model()

    # Variable to store path of uploaded files
    # uploaded_files = []

    # Creating a session id 
    session_id = str(uuid.uuid4())

    try:

    # ----------------------------------------------------------------------------------------------------
    #  Session creation, and storing in db , Jd embedding, chroma db collection storage
    # -----------------------------------------------------------------------------------------------------
 
        #Creating a session_name

        jd_prompt = get_prompt_session_name(jd)

        title_response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": jd_prompt}],
                model="llama-3.1-8b-instant", # Groq supports Llama 3!
            )

        session_name = title_response.choices[0].message.content.strip()

        # Storing jd and session_id

        session = session_repo.add_session_details(
            session_id=session_id,
            session_name=session_name,
            jd_description=jd
        )

        if not session:
            raise HTTPException(
                status_code = 500,
                detail = "Error adding session details"
            )


        # --------------------------------------------------------------
        # Converting files into dictionary format
        # --------------------------------------------------------------

        files_data = []

        if drive_link:
            files_data = extract_files_from_drive(drive_link)


        if files:
            for file in files:
                files_data.append(
                    {
                        "filename": file.filename,
                        "content": await file.read()
                    }
                )
        

        # Extracting top 10 resumes

        result = await extract_top_from_files(
            session_id=session_id,
            files_data=files_data,
            jd=jd
        )

        search_results = result["search_results"]
        resume_data = result["resume_data"]
            


    # ----------------------------------------------------------------------------------------------
    #  Retriving top resumes using jd embedding
    # --------------------------------------------------------------------------------------------------
        

        # two variables to store rows to be inserted in db
        chunk_rows = []
        resume_data_rows = []


    # -----------------------------------------------------------------------
    # Evaluating shortisted resumes and storing required results in db
    # ------------------------------------------------------------------------



        # Use Groq LLM to evaluate the shortlisted resumes
        for i in range(len(search_results['ids'][0])):

            res_id = search_results['ids'][0][i]
            res_text = search_results['documents'][0][i]
            filename = search_results['metadatas'][0][i]['filename']
            extension = Path(filename).suffix.lower()


            file_content = resume_data[res_id]["content"]
            file_path = f"{session_id}/{res_id}{extension}"
            
            # Storing file in db
            response = files_repo.store_file(file_path , file_content)

            if not response:
                raise Exception(f"Failed to upload file {filename} to storage bucket.")



            candidate_details = extract_details(res_text)

            print(f"Get evaluation metrics for {candidate_details['name']}\n")

            # Using Groq LLM to evaluate the resume against the job description
            evaluation = evaluation_chain.invoke(
                {
                "jd": jd,
                "res_text": res_text
                }
            ).model_dump()




            

            # Removing if any duplicate matched skills returned
            skills = evaluation["top_matched_skills"]
            skills = list(dict.fromkeys(skills))
            evaluation["top_matched_skills"] = skills


            #Removing if any duplicate missing skills returned
            mis_skills = evaluation["missing_skills"]
            mis_skills = list(dict.fromkeys(mis_skills))
            evaluation["missing_skills"] = mis_skills

            # Calculating final match score
            breakdown = evaluation["score_breakdown"]

            match_score = round(
                breakdown["technical_skills"] * 0.35
                + breakdown["professional_experience"] * 0.25
                + breakdown["project_evidence"] * 0.20
                + breakdown["education_and_training"] * 0.10
                + breakdown["domain_relevance"] * 0.10
            )


            # Storing all data in db
            resume_data_rows.append({
                "resume_id" : str(res_id),
                "session_id" : session_id,

                "name":candidate_details['name'],
                "email": candidate_details["email"],
                "contact": candidate_details["phone"],

                "score": match_score,
                "summary": evaluation["summary"],
                "matched_skills": evaluation["top_matched_skills"],
                "missing_skills": evaluation["missing_skills"],

                "file_url" : file_path
            })



            print(f"Storing resume data for {candidate_details['name']} in list\n")

            chunks = splitter.split_text(res_text)
            chunk_embeddings = embedding_model.encode(
                chunks
            ).tolist()

            for idx, (chunk, chunk_embedding) in enumerate(
                zip(chunks, chunk_embeddings)):

                chunk_rows.append(
                    {
                        "session_id" : session_id,
                        "resume_id" : res_id,
                        "chunk_text" : chunk,
                        "embedding" : chunk_embedding,
                        "candidate_name" : candidate_details["name"],
                        "chunk_index" : idx
                    }
                )


            print(f"Storing chunks for {candidate_details['name']} in list\n\n")
            
                # If both rows array have data then push it into respective db
        
        
        # After all looping done, storing results

        if resume_data_rows:    
            response = resume_repo.add_resume_data(resume_data_rows)
            if response is None:
                raise Exception("Failed to add resume data to the database.")


        if chunk_rows:
            response = resume_chunks_repo.add_resume_chunks(chunk_rows)
            if response is None:
                raise Exception("Failed to add chunk data to the database.")

        # Deleting collection because no longer needed
        chroma_client.delete_collection(
            name=f"session_{session_id}"
        )
        
        
        # Return the current session_id
        return {
            "session_id": session_id
        }


    except Exception as e:

        print(f"Upload session failed : {e}")

        # Deleting if any chunks uploaded in db
        try:
            resume_chunks_repo.delete_resume_chunks_by_session(session_id)
        except:
            pass
        
        
        #  Deleting if any resume data uploaded in db
        try:
            resume_repo.delete_resume_data_by_session(session_id)
        except:
            pass

        # Deleting if any sessions data uploaded in db
        try:
            session_repo.delete_session_by_id(session_id)
        except:
            pass
        
        # Deleting if any files uploaded in db
        try:
            files_repo.delete_session_files(session_id)
        except:
            pass

        # Deleting the croma collection
        try:
            chroma_client.delete_collection(
                name=f"session_{session_id}"
            )
        except:
            pass
        
        # Raising exception
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


