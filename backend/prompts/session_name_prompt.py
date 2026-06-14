
def get_prompt_session_name(jd):
    return f"""
    You generate session titles for a resume screening application.
    
    Rules:
    - Create a concise but specific title (4-8 words).
    - Capture the role, seniority, and key technologies from the job description.
    - Avoid generic titles like "Resume Screening", "Hiring Session", or "Job Analysis".
    - Prefer format:
    
    <Role> | <Key Skills>
    
    Examples:
    - Senior Python Developer | FastAPI & AWS
    - Data Scientist | NLP & Machine Learning
    - Frontend Engineer | React & TypeScript
    - DevOps Engineer | Kubernetes & Azure
    
    Return ONLY the title.
    
    Job Description:
    {jd}
    """