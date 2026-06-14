from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.text_splitter import splitter
from services.vector_db_store import chroma_client
from services.embedding_model import embedding_model
from services.llm_initialization import groq_client
from services.supabase_client import supabase, bucket_name

from utils.extract_candidate_details import extract_details
from utils.text_extraction_util import extract_text_from_pdf

from prompts.upload_resume_prompt import get_evaluation_prompt
from prompts.session_name_prompt import get_prompt_session_name

import json
from typing import List

import uuid

router = APIRouter()

@router.post("/api/upload")
async def upload_and_screen(
    jd: str = Form(...),
    files: List[UploadFile] = File(...) ):

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


        # 1. Embed the Job Description
        jd_embedding = embedding_model.encode(jd).tolist()


        # Create collection for new batch
        collection = chroma_client.get_or_create_collection(
            name=f"session_{session_id}"
        )


        # Variable to store resume paths
        resume_data = {}

        # 2. Parse and Embed Resumes
        for i, file in enumerate(files):
            content = await file.read()
            text = extract_text_from_pdf(content)
            resume_id = str(uuid.uuid4())

             # Keep PDF and text in memory for now
            resume_data[resume_id] = {
                "content": content,
                "text": text,
                "filename": file.filename
            }


            # Add to Vector DB
            embedding = embedding_model.encode(text).tolist()
            collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[{"filename": file.filename, "type": "resume"}],
                ids=[resume_id]
            )


    # ----------------------------------------------------------------------------------------------
    #  Retriving top resumes using jd embedding
    # --------------------------------------------------------------------------------------------------

        # 3. Find top semantic matches using Vector DB
        search_results = collection.query(
            query_embeddings=[jd_embedding],
            n_results=min(10, len(files)) # Get top 3 for this example
        )

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

            # prompt for resume evaluation
            prompt = get_evaluation_prompt(jd , res_text)


            pdf_content = resume_data[res_id]["content"]
            file_path = f"{session_id}/{res_id}.pdf"

            supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=pdf_content,
                file_options={
                    "content-type": "application/pdf"
                }
            )

            uploaded_files.append(file_path)

            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", # Groq supports Llama 3!
                response_format={"type": "json_object"}
            )

            evaluation = json.loads(chat_completion.choices[0].message.content)
            candidate_details = extract_details(res_text)

            # Removing if any duplicate matched skills returned
            skills = evaluation["top_matched_skills"]
            skills = list(dict.fromkeys(skills))
            evaluation["top_matched_skills"] = skills


            #Removing if any duplicate missing skills returned
            mis_skills = evaluation["missing_skills"]
            mis_skills = list(dict.fromkeys(mis_skills))
            evaluation["missing_skills"] = mis_skills


            # Storing all data in db
            resume_data_rows.append({
                "resume_id" : str(res_id),
                "session_id" : session_id,

                "name":candidate_details['name'],
                "email": candidate_details["email"],
                "contact": candidate_details["phone"],

                "score": evaluation["match_score"],
                "summary": evaluation["summary"],
                "matched_skills": evaluation["top_matched_skills"],
                "missing_skills": evaluation["missing_skills"],

                "pdf_url" : file_path
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


