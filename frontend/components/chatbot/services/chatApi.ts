import axios from "axios";

const API_URL = "http://127.0.0.1:8000";




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
  sessionID: string
) {
  return axios.post(
    `${API_URL}/api/email/regenerate`,
    {
      draft_id: draftId,
      session_id: sessionID
    }
  );
}



export async function sendEmail(
  draftId: number,
  sessionID: string
) {
  return axios.post(
    `${API_URL}/api/email/send`,
    {
      draft_id: draftId,
      session_id: sessionID
    }
  );
}

