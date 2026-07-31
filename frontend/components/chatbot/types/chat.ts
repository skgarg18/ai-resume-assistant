export type MeetingMetadata = {
  date: string | null;
  time: string | null;
  comments: string | null;
  requires_meeting_link: boolean;
};


export interface CandidateSearchCandidate {
  id: string;
  match_significance?: string;
}

interface CandidateSearchDetails {
  type: "candidate_search";
  candidates: CandidateSearchCandidate[];
}

export interface CandidateLookupResult {
  resume_id: string;
  bullet_points: string[]; // Change to bullet_points if you keep that field name
}

interface CandidateLookupDetails{
  type : "candidate_lookup";
  candidates: CandidateLookupResult[];
  missing_names: string[];
}

type ChatDetails =
  | CandidateSearchDetails
  |CandidateLookupDetails
  ;


 
export interface EmailCandidate {
  resume_id?: string | null;
  name: string;
  email: string;
  match_score?: number | null;
}  



export type Message =
  | {
      role: "user";
      content: string;
    }
  | {
      role: "assistant";
      type: "chat";
      content: string;
      details?: ChatDetails;
    }
  | {
      role: "assistant";
      type: "email";

      draft_id: string;

      email_candidates: EmailCandidate[];
      selected_email_candidate: EmailCandidate;

      subject: string;
      body: string;

      meeting_metadata?: MeetingMetadata;

      cc_emails: string[];

      bcc_emails: string[];
    };