export type MeetingMetadata = {
  date: string | null;
  time: string | null;
  comments: string | null;
  requires_meeting_link: boolean;
};



export type Message =
  | {
      role: "user";
      content: string;
    }
  | {
      role: "assistant";
      type: "chat";
      content: string;
    }
  | {
      role: "assistant";
      type: "email";

      draft_id: string;

      email_ids: string[];
      subject: string;
      body: string;

      selected_email: string;

      meeting_metadata?: MeetingMetadata;
    };