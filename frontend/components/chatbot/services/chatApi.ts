import api from '@/lib/axios';


import {EmailMeetingDetails} from '../components/EmailCard'
import {EmailCandidate} from "../types/chat"

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
  email_candidates: EmailCandidate[],
  selected_email_candidate:EmailCandidate,
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
      candidates: email_candidates,
      selected_candidate : selected_email_candidate,
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
  selected_email_candidate: EmailCandidate,
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
      selected_candidate:selected_email_candidate,
      ccEmails: ccEmails,
      bccEmails:bccEmails
    }
  );
}

