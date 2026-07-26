from logs.log_context import get_logger


import os
import smtplib
import socket
import ssl
import markdown 
from email.message import EmailMessage


from logs.log_context import get_logger

def send_email(
    to_email: str,
    subject: str,
    body: str,
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
) -> str:
    logger = get_logger()

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        logger.error("SMTP credentials are missing.")
        return "Failed: Email service is not configured."

    cc_emails = cc_emails or []
    bcc_emails = bcc_emails or []

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)

        # Plain text version
        msg.set_content(body)

        # HTML version
        html_body = markdown.markdown(
            body,
            extensions=["nl2br", "sane_lists"]
        )
        msg.add_alternative(html_body, subtype="html")

        # BCC recipients are NOT added to headers
        recipients = [to_email] + cc_emails + bcc_emails

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg, to_addrs=recipients)

        logger.info(f"Email sent successfully to {to_email}")
        return "Success"

    except smtplib.SMTPRecipientsRefused as e:
        logger.exception(f"Recipient rejected by mail server: {e.recipients}")
        return "Failed: Invalid recipient email address."

    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed.")
        return "Failed: Unable to send email. Please try again later."

    except smtplib.SMTPSenderRefused:
        logger.exception("Sender address refused by SMTP server.")
        return "Failed: Unable to send email. Please try again later."

    except smtplib.SMTPDataError:
        logger.exception("SMTP server rejected the email content.")
        return "Failed: Unable to send email. Please try again later."

    except smtplib.SMTPConnectError:
        logger.exception("Could not connect to SMTP server.")
        return "Failed: Unable to send email. Please try again later."

    except smtplib.SMTPServerDisconnected:
        logger.exception("SMTP server disconnected unexpectedly.")
        return "Failed: Unable to send email. Please try again later."

    except socket.timeout:
        logger.exception("SMTP connection timed out.")
        return "Failed: Unable to send email. Please try again later."

    except socket.gaierror:
        logger.exception("Failed to resolve SMTP server hostname.")
        return "Failed: Unable to send email. Please try again later."

    except ssl.SSLError:
        logger.exception("SSL error while communicating with SMTP server.")
        return "Failed: Unable to send email. Please try again later."

    except smtplib.SMTPException:
        logger.exception("Unexpected SMTP exception.")
        return "Failed: Unable to send email. Please try again later."

    except Exception:
        logger.exception("Unexpected error while sending email.")
        return "Failed: Unable to send email. Please try again later."

def send_completion_email(to_email:str , succesful:int , failed:int , link:str):

    logger = get_logger()

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
            "Succesfully sent mail for success in processing"
        )
        
    except Exception :
        logger.exception(
            "Failed to send completion email"
        )

        return False

    return True



def send_failure_email(to_email:str , succesful:int , failed:int):

    logger = get_logger()

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
            "Succesfully sent mail for failure in processing"
        )
    
    except Exception:
        logger.exception(
            "Failed to send failure email"
        )

        return False
        


    return True


