# utils/tool_execution_util.py
import json
import re
from datetime import datetime, timedelta
import pytz
from services.candidate_service import get_candidate_email
from services.email_service import send_interview_email
from services.zoom_service import generate_zoom_link

def execute_email_tool(tool_call, session_id: str) -> str:
    args = json.loads(tool_call.function.arguments)
    
    # Fallback to handle if it sends candidate_email instead of candidate_name
    candidate_name = args.get("candidate_name") or args.get("candidate_email", "").split("@")[0].replace(".", " ").title()
    subject = args.get("subject", f"Interview Invitation for {candidate_name}")
    email_body = args.get("email_body", "")
    
    ist = pytz.timezone('Asia/Kolkata')
    current_year = "2026" # Hardcoded guardrail for temporal synchronization
    
    start_time_iso = args.get("start_time_iso")
    end_time_iso = args.get("end_time_iso")
    
    # --- TEMPORAL RECOVERY GUARDRAIL ---
    if start_time_iso:
        # If the model hallucinates a past year, force it to 2026
        if not start_time_iso.startswith(current_year):
            start_time_iso = current_year + start_time_iso[4:]
    else:
        tomorrow = datetime.now(ist) + timedelta(days=1)
        start_time_iso = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
        
    if end_time_iso:
        if not end_time_iso.startswith(current_year):
            end_time_iso = current_year + end_time_iso[4:]
    else:
        start_dt = datetime.fromisoformat(start_time_iso)
        end_time_iso = (start_dt + timedelta(minutes=30)).isoformat()
    # ------------------------------------

    # Handle nested JSON object structure if present
    if isinstance(email_body, dict) and "body" in email_body:
        email_body = email_body["body"]
    elif isinstance(email_body, str):
        try:
            parsed_body = json.loads(email_body)
            if isinstance(parsed_body, dict) and "body" in parsed_body:
                email_body = parsed_body["body"]
        except json.JSONDecodeError:
            pass

    candidate_email = get_candidate_email(session_id, candidate_name)
    if not candidate_email:
        # Fallback query attempt just in case the raw extraction was an email
        if "@" in args.get("candidate_email", ""):
            candidate_email = args.get("candidate_email")
        else:
            return f"Could not find an email address for candidate '{candidate_name}'."

    # 1. Generate the REAL meeting link via Zoom API (Now safely with a 2026 timestamp)
    meet_link = generate_zoom_link(candidate_name, start_time_iso, end_time_iso)
    
    # 2. Complete Link Injection Strategy
    email_body = email_body.replace("\\n", "\n")
    if "[MEETING_LINK]" in email_body:
        email_body = email_body.replace("[MEETING_LINK]", meet_link)
    elif "Zoom meeting link:" in email_body:
        email_body = re.sub(r"Zoom meeting link:.*", f"Zoom meeting link: {meet_link}", email_body)
    elif "Interview Location:" in email_body:
        email_body = re.sub(r"Interview Location:.*", f"Interview Location: {meet_link}", email_body)
    else:
        email_body = f"{email_body.strip()}\n\nZoom Meeting Link: {meet_link}"

    # 3. Dispatched to Email Service
    result_status = send_interview_email(
        to_email=candidate_email, 
        subject=subject,
        body=email_body
    )
    
    if result_status == "Success":
        return (
            "Email sent successfully. "
            "CRITICAL INSTRUCTION: Your final response to the user MUST ONLY be the following text block. Do not add any conversational text before or after it.\n\n"
            f"```text\n"
            f"Subject: {subject}\n\n"
            f"{email_body}\n"
            f"```"
        )
    else:
        return result_status