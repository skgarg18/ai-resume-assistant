import logging
from time import perf_counter

logger = logging.getLogger(__name__)

import os
import smtplib
import markdown 
from email.message import EmailMessage

def send_email(to_email: str, subject: str, body: str) -> str:
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        return "Failed: Missing SMTP credentials."
    


    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        
        # 1. Set the plain text fallback (for older email clients)
        msg.set_content(body)
        
        # 2. Convert the LLM's Markdown to HTML and add it as an alternative
        html_body = markdown.markdown(body, extensions=['nl2br', 'sane_lists'])
        
        msg.add_alternative(html_body, subtype='html')
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        
        return f"Success"
        
    except Exception as e:
        return f"Failed to send email: {str(e)}"


def send_completion_email(to_email:str , succesful:int , failed:int , link:str , session_id:str):

    subject="Scanning of resumes done succesfully"
    
    body=f"""
Hi,

Your resume scanning job has completed successfully.

Summary:
- Successfully processed: {succesful}
- Failed: {failed}

You can now open the application to view the shortlisted candidates.

Link:
{link}

Regards,
Resume AI
"""
    
    try:
        send_email(
            to_email=to_email,
            subject=subject,
            body=body
        )

        logger.info(
            "Succesfully sent mail for success in processing | session_id=%s",
            session_id
        )
        
    except Exception :
        logger.exception(
            "Failed to send completion email | session_id=%s",
            session_id,
        )

        return False

    return True



def send_failure_email(to_email:str , succesful:int , failed:int , session_id:str):

    subject="Scanning of resumes failed"

    body=f"""
Hi,

Your resume scanning job has failed due to unexpected error

Summary:
- Successfully processed: {succesful}
- Failed: {failed}

Regards,
Resume AI
    """

    try:
        send_email(to_email=to_email , subject=subject , body=body)

        logger.info(
            "Succesfully sent mail for failure in processing | session_id=%s",
            session_id
        )
    
    except Exception:
        logger.exception(
            "Failed to send failure email | session_id=%s",
            session_id
        )

        return False
        


    return True


