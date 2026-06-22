"use client";

interface EmailCardProps {
  draft_id: number;

  email_id: string;

  subject: string;

  body: string;

  onRegenerate: (
    draftId: number
  ) => void;

  onSend: (
    draftId: number
  ) => void;
}

import ReactMarkdown from "react-markdown";

export default function EmailCard({
  draft_id,
  email_id,
  subject,
  body,
  onRegenerate,
  onSend,
}: EmailCardProps) {
  return (
    <div className="space-y-3 w-full">

      <div>
        <span className="font-semibold">
          To:
        </span>{" "}
        {email_id}
      </div>

      <div>
        <span className="font-semibold">
          Subject:
        </span>{" "}
        {subject}
      </div>

      <div className="whitespace-pre-wrap text-sm leading-relaxed">
        <ReactMarkdown>
          {body}
        </ReactMarkdown>
        
      </div>

      <div className="flex gap-2 pt-2">

        <button
          onClick={() =>
            onRegenerate(draft_id)
          }
          className="
            px-3
            py-1.5
            rounded-lg
            bg-gray-200
            hover:bg-gray-300
            text-sm
            transition
            cursor-pointer
          "
        >
          Regenerate
        </button>

        <button
          onClick={() =>
            onSend(draft_id)
          }
          className="
            px-3
            py-1.5
            rounded-lg
            bg-blue-600
            text-white
            hover:bg-blue-700
            text-sm
            transition
            cursor-pointer
          "
        >
          Send
        </button>

      </div>
    </div>
  );
}