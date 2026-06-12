from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.text_splitter import splitter
from services.vector_db_store import collection , chat_collection
from services.embedding_model import embedding_model
from services.llm_initialization import groq_client

from utils.extract_candidate_details import extract_details
from utils.text_extraction_util import extract_text_from_pdf

from prompts.upload_resume_prompt import get_evaluation_prompt
import json
from typing import List



router = APIRouter()

@router.post("/api/upload")
async def upload_and_screen(
    jd: str = Form(...),
    files: List[UploadFile] = File(...)
):
    # Declaring two arrays to return in result, one to store top resumes and other to store names
    results = []
    names = []
    
    # 1. Embed the Job Description
    jd_embedding = embedding_model.encode(jd).tolist()
    
    # Clear collection for new batch
    if collection.count() > 0:
        collection.delete(where={"type": "resume"})


    # Clear if any chat collection
    if chat_collection.count() > 0:
        
        existing = chat_collection.get()

        if existing["ids"]:
            chat_collection.delete(
                ids=existing["ids"]
            )

    parsed_resumes = {}

    # 2. Parse and Embed Resumes
    for i, file in enumerate(files):
        content = await file.read()
        text = extract_text_from_pdf(content)
        resume_id = f"resume_{i}_{file.filename}"
        
        parsed_resumes[resume_id] = text
        
        # Add to Vector DB
        embedding = embedding_model.encode(text).tolist()
        collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"filename": file.filename, "type": "resume"}],
            ids=[resume_id]
        )

    # 3. Find top semantic matches using Vector DB
    search_results = collection.query(
        query_embeddings=[jd_embedding],
        n_results=min(10, len(files)) # Get top 3 for this example
    )

    # 4. Use Groq LLM to evaluate the shortlisted resumes
    for i in range(len(search_results['ids'][0])):
        res_id = search_results['ids'][0][i]
        res_text = search_results['documents'][0][i]
        filename = search_results['metadatas'][0][i]['filename']
        
        prompt = get_evaluation_prompt(jd , res_text)
        
        try:
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

            

            results.append({
                "id": res_id,
                "filename": filename,
                "evaluation": evaluation,
                "raw_text": res_text,
                "details" : candidate_details
            })
            

            names.append(candidate_details['name'])

            chunks = splitter.split_text(res_text)

            for idx, chunk in enumerate(chunks):
            
                chunk_embedding = embedding_model.encode(
                    chunk
                ).tolist()

                chat_collection.add(
                    ids=[f"{res_id}_{idx}"],
                    embeddings=[chunk_embedding],
                    documents=[chunk],
                    metadatas=[{
                        "candidate": candidate_details['name'],
                        "resume_id": res_id,
                        "filename": filename
                    }]
                )

        except Exception as e:
            print(f"Error evaluating {filename}: {e}")

    # Sort results by score
    results = sorted(results, key=lambda x: x['evaluation'].get('match_score', 0), reverse=True)

    return {
        "shortlist": results ,
        "candidate_names" : names
        }