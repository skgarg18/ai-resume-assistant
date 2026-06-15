# schema/tool_schemas.py

EMAIL_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "send_interview_email",
        "description": "CRITICAL: ONLY call this tool if the user EXPLICITLY asks to send an email, schedule an interview, or invite a candidate. DO NOT call this tool for general chat.",
        "parameters": {
            "type": "object",
            "properties": {
                "candidate_name": {
                    "type": "string",
                    "description": "The exact structural NAME of the candidate to email (e.g., 'Shubham K Garg'). DO NOT put an email address here."
                },
                "subject": {"type": "string"},
                "email_body": {
                    "type": "string", 
                    "description": "The plain text body of the email. DO NOT wrap this in a JSON object. Just write the raw text. Use '\\n\\n' for paragraphs. Include '[MEETING_LINK]' where the Zoom link belongs."
                },
                "start_time_iso": {
                    "type": "string",
                    "description": "Valid ISO 8601 format string. Ensure the year matches the current year 2026."
                },
                "end_time_iso": {
                    "type": "string",
                    "description": "Valid ISO 8601 format string. Ensure the year matches the current year 2026."
                }
            },
            "required": ["candidate_name", "subject", "email_body"]
        }
    }
}