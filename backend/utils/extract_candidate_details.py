from services.llm_initialization import groq_client
import json

import re

def extract_name(resume_text):

    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

    blacklist = {
        "resume",
        "curriculum vitae",
        "cv",
        "professional summary",
        "summary",
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",
        "achievements",
        "contact",
        "profile",
        "objective"
    }

    job_titles = {
        "software engineer",
        "software developer",
        "full stack developer",
        "frontend developer",
        "backend developer",
        "data scientist",
        "machine learning engineer",
        "devops engineer",
        "project manager",
        "business analyst"
    }

    for line in lines[:15]:

        lower = line.lower().strip()

        if lower in blacklist or lower in job_titles:
            continue

        if any(x in lower for x in [
            "@",
            "linkedin",
            "github",
            "email",
            "phone",
            "mobile",
            "location",
            "www"
        ]):
            continue

        if len(re.findall(r"\d", line)) >= 3:
            continue

        # Remove common prefixes FIRST
        cleaned = re.sub(
            r'^(name|candidate name)\s*:\s*',
            '',
            line,
            flags=re.IGNORECASE
        ).strip()

        cleaned = re.sub(r"[^A-Za-z.\s]", "", cleaned).strip()

        words = cleaned.split()

        if 2 <= len(words) <= 4:

            if all(len(word) > 1 for word in words):

                # Optional: make display prettier
                return cleaned.title()

    return None

def extract_email(resume_text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    match = re.search(pattern, resume_text)
    return match.group(0) if match else None


def extract_phone(text):
    pattern = r'(?:\+91[-\s]?)?[0-9][0-9\s\-]{8,15}'

    matches = re.findall(pattern, text)

    for match in matches:
        phone = re.sub(r'\D', '', match)

        if len(phone) == 10:
            return f"{phone[:5]} {phone[5:]}"

        if len(phone) == 12:
            return f"+{phone[:2]} {phone[2:7]} {phone[7:]}"

        return phone

    return None


def extract_details(res_text):

    data = {}

    data['name'] = extract_name(res_text) or ""
    data['email'] = extract_email(res_text) or ""
    data['phone'] = extract_phone(res_text) or ""

    return data


