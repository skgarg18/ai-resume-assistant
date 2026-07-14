from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from pathlib import Path

from services.text_splitter import splitter
from services.vector_db_store import chroma_client
from services.embedding_model import get_embedding_model
from services.llm_initialization import groq_client
from services.supabase_client import supabase, store_file_in_bucket

from utils.extract_candidate_details import extract_details

from prompts.session_name_prompt import get_prompt_session_name

from routers.upload_file_router.chains.evaluation_chain import evaluation_chain

from routers.upload_file_router.extractions.extracting_from_files import extract_top_from_files
from routers.upload_file_router.extractions.extract_from_drive import extract_files_from_drive
import json
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
    uploaded_files = []

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
        supabase.table("sessions").insert({
            "session_id": session_id,
            "session_name": session_name,
            "job_description": jd
        }).execute()


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
            

            store_file_in_bucket(file_path , file_content)

            uploaded_files.append(file_path)


            
            evaluation = evaluation_chain.invoke(
                {
                "jd": jd,
                "res_text": res_text
                }
            ).model_dump()

            # print(evaluation)

            candidate_details = extract_details(res_text)

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
            
                # If both rows array have data then oush it into respective db
        
        
        # After all looping done, storing results

        if resume_data_rows:
            supabase.table("resumes").insert(resume_data_rows).execute()
        if chunk_rows:
            supabase.table("resume_chunks").insert(chunk_rows).execute()
        

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
            supabase.table("resume_chunks")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
        except:
            pass
        
        
        #  Deleting if any resume data uploaded in db
        try:
            supabase.table("resumes")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
        except:
            pass

        # Deleting if any sessions data uploaded in db
        try:
            supabase.table("sessions")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
        except:
            pass
        
        # Deleting if any files uploaded in db
        try:
            if uploaded_files:
                supabase.storage.from_(bucket_name).remove(
                    uploaded_files
                )
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


