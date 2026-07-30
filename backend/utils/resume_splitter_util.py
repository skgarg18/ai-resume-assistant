"""
Utility for chunking resume documents cleanly without breaking bullet points or headers.
"""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_resume_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    Configures a RecursiveCharacterTextSplitter tailored specifically for resumes.
    Respects section headers, double line breaks, and bullet points (•, -).
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=500,        # Keeps chunks (~80-100 words) dense and focused
        chunk_overlap=100,     # Preserves context across chunk boundaries
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",            # Section gaps (e.g., between EXPERIENCE and EDUCATION)
            "\n",              # Line breaks
            "• ",              # Resume bullet points
            "- ",              # Alternative bullet points
            "; ",              # Skill lists
            ". ",              # Sentence breaks
            " ",               # Word breaks
            ""
        ]
    )


def split_resume_into_chunks(
    resume_id: str,
    candidate_name: str,
    session_id: str,
    raw_resume_text: str
) -> List[Dict[str, Any]]:
    """
    Splits raw resume text into structured chunk rows ready for DB insertion.
    """
    if not raw_resume_text or not raw_resume_text.strip():
        return None

    splitter = create_resume_text_splitter()
    text_chunks = splitter.split_text(raw_resume_text)

    chunk_rows = []
    for index, chunk_text in enumerate(text_chunks):
        cleaned_text = chunk_text.strip()
        if not cleaned_text:
            continue

        chunk_rows.append({
            "session_id": session_id,
            "resume_id": resume_id,
            "candidate_name": candidate_name,
            "chunk_index": index,
            "chunk_text": cleaned_text
        })

    return chunk_rows