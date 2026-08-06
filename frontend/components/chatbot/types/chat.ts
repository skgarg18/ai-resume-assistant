// ============================================================================
// 1. MEETING METADATA WORKFLOW
// ============================================================================

export type MeetingMetadata = {
  date: string | null;
  time: string | null;
  comments: string | null;
  requires_meeting_link: boolean;
};

// ============================================================================
// 2. CANDIDATE SEARCH WORKFLOW
// ============================================================================

export interface CandidateSearchCandidate {
  id: string;
  match_significance?: string;
}

interface CandidateSearchDetails {
  type: "candidate_search";
  candidates: CandidateSearchCandidate[];
}

// ============================================================================
// 3. CANDIDATE LOOKUP WORKFLOW
// ============================================================================

export interface CandidateLookupResult {
  resume_id: string;
  bullet_points: string[]; // Change to bullet_points if you keep that field name
}

interface CandidateLookupDetails {
  type: "candidate_lookup";
  candidates: CandidateLookupResult[];
  missing_names: string[];
}

// ============================================================================
// 4. CANDIDATE COMPARISON WORKFLOW
// ============================================================================

export interface ComparisonCard {
  title: string;
  candidate_1: string;
  candidate_2: string;
  verdict: string;
}

export interface CandidateComparisonData {
  candidates: string[];
  summary: string;
  winner: string;
  recommendation: string;
  strengths_candidate_1: string[];
  strengths_candidate_2: string[];
  comparison: ComparisonCard[];
}

interface CandidateComparisonDetails {
  type: "candidate_comparison";
  data: CandidateComparisonData;
}

// ============================================================================
// 5. CHAT DETAILS DISCRIMINATED UNION
// ============================================================================

type ChatDetails =
  | CandidateSearchDetails
  | CandidateLookupDetails
  | CandidateComparisonDetails;

// ============================================================================
// 6. EMAIL WORKFLOW
// ============================================================================

export interface EmailCandidate {
  resume_id?: string | null;
  name: string;
  email: string;
  match_score?: number | null;
}

// ============================================================================
// 7. CORE MESSAGE WORKFLOW & PAYLOADS
// ============================================================================

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