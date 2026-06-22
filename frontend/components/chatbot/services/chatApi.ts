import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

import {EmailMeetingDetails} from '../components/EmailCard'


export async function sendChatMessage(
  sessionID: string,
  payload: any
) {
  return axios.post(
    `${API_URL}/api/${sessionID}/chat`,
    payload
  );
}



export async function regenerateEmail(
  draftId: number,
  sessionID: string,
  appliedDetails : EmailMeetingDetails
) {
  return axios.post(
    `${API_URL}/api/email/regenerate`,
    {
      draft_id: draftId,
      session_id: sessionID,
      details: appliedDetails
    }
  );
}



export async function sendEmail(
  draftId: number,
  sessionID: string,
  appliedDetails: EmailMeetingDetails
) {
  return axios.post(
    `${API_URL}/api/email/send`,
    {
      draft_id: draftId,
      session_id: sessionID,
      details: appliedDetails
    }
  );
}

