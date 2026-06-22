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
    };