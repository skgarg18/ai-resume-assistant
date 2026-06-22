import os
import smtplib
import markdown 
from email.message import EmailMessage

def send_interview_email(to_email: str, subject: str, body: str) -> str:
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