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

      draft_id: number;

      email_id: string;
      subject: string;
      body: string;

      meeting_metadata?: MeetingMetadata;
    };