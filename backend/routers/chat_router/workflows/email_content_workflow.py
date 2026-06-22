from routers.chat_router.chains.email_content_chian import email_chain

from services.supabase_client import supabase

from services.candidate_service import get_candidate_email

async def email_content_workflow(question : str , candidate_names : list[str] , session_id:str):


    if not candidate_names:
        candidate_email = ""
    
    else:
        candidate_email = get_candidate_email(session_id , candidate_names[0]) or ""

    response = email_chain.invoke(
        {
            "question" : question
        }
    )
 

    result = supabase.table("email_drafts").insert({
        "session_id": session_id,
        "candidate_name": candidate_names[0] if candidate_names else None,
        "recipient_email": candidate_email,
        "subject": response.subject,
        "body": response.body,
        "status": "draft",
        "original_prompt": question,
        "meeting_metadata": response.meeting_details.model_dump(),
    }).execute()


    supabase.table("chat_history").insert({
        "session_id" : session_id,
        "user_message" : question,
        "email_id": candidate_email,
        "email_subject": response.subject,
        "email_body": response.body,
        "draft_id" : result.data[0]['id'],
        "message_type" : "email",
        "email_meeting_metadata" : response.meeting_details.model_dump(),
    }).execute()


    if not result.data:
        raise Exception("Failed to create email draft")



    return{
        "draft_id" : result.data[0]['id'],
        "type" : "email",
        "email_id" : candidate_email,
        "subject" : response.subject,
        "body" : response.body,

        "meeting_metadata" : response.meeting_details.model_dump() ,

        "actions": [
            "regenerate",
            "add_details",
            "send"
        ]
    }

