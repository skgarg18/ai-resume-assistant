import api from '@/lib/axios';


import {EmailMeetingDetails} from '../components/EmailCard'


export async function sendChatMessage(
  sessionID: string,
  payload: any
) {
  return api.post(
    `/api/${sessionID}/chat`,
    payload
  );
}



export async function regenerateEmail(
  draftId: string,
  sessionID: string,
  appliedDetails : EmailMeetingDetails,
  body: string,
  subject: string,
  email_ids: string[],
  selected_email:string,
  cc_emails: string[],
  bcc_emails: string[]
) {
  return api.post(
    `/api/email/regenerate`,
    {
      draft_id: draftId,
      session_id: sessionID,
      details: appliedDetails,
      body: body,
      subject: subject,
      email_ids: email_ids,
      selected_email : selected_email,
      cc_emails: cc_emails,
      bcc_emails: bcc_emails
    }
  );
}



export async function sendEmail(
  draftId: string,
  sessionID: string,
  appliedDetails: EmailMeetingDetails,
  subject: string,
  body: string,
  selected_email: string,
  ccEmails : string[],
  bccEmails: string[]

) {
  return api.post(
    `/api/email/send`,
    {
      draft_id: draftId,
      session_id: sessionID,
      details: appliedDetails,
      subject: subject,
      body: body,
      selected_email:selected_email,
      ccEmails: ccEmails,
      bccEmails:bccEmails
    }
  );
}

