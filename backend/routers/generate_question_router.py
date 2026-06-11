from fastapi import APIRouter
from schema.question_schema import QuestionRequest
from services.llm_initialization import groq_client

router = APIRouter()

@router.post("/api/generate_questions")
async def generate_questions(req: QuestionRequest):
    prompt = f"""
    Act as a hiring manager. Based on this Job Description and the Candidate's Resume, 
    generate 3 specific technical questions and 2 behavioral questions to ask them in an interview.
    Make the questions highly specific to the claims on their resume.
    
    Job Description: {req.jd}
    Resume: {req.resume_text}
    """
    
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    
    return {"questions": chat_completion.choices[0].message.content}
