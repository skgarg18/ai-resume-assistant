"use client";

import { Send } from "lucide-react";

interface ChatInputProps {
  question: string;

  setQuestion: (
    value: string
  ) => void;

  loading: boolean;

  sendMessage: () => void;

  suggestedQuestions: string[];
}

export default function ChatInput({
  question,
  setQuestion,
  loading,
  sendMessage,
  suggestedQuestions,
}: ChatInputProps) {

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col gap-2 p-2 border-t bg-white shrink-0">

      {/* Suggested Questions */}

      <div>
        {suggestedQuestions.length > 0 && (

          <div className="flex flex-wrap gap-2">

            {suggestedQuestions.map((q) => (

              <button
                key={q}
                onClick={() =>
                  setQuestion(q)
                }
                className="
                  text-xs
                  bg-blue-50
                  text-blue-700
                  hover:bg-blue-100
                  px-1
                  py-1.5
                  rounded-full
                  transition
                  font-medium
                "
              >
                {q}
              </button>

            ))}

          </div>

        )}
      </div>

      {/* Input */}

      <div
        className="
          flex
          gap-2
          items-center
          bg-gray-50
          border
          rounded-xl
          px-2
          py-1
          focus-within:ring-2
          focus-within:ring-blue-500
          focus-within:border-transparent
          transition-all
        "
      >

        <input
          type="text"
          value={question}
          onChange={(e) =>
            setQuestion(
              e.target.value
            )
          }
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about the resumes..."
          className="
            flex-1
            bg-transparent
            px-2
            py-1
            text-sm
            outline-none
          "
        />

        <button
          onClick={sendMessage}
          disabled={
            loading ||
            !question.trim()
          }
          className="
            bg-blue-600
            text-white
            p-2
            rounded-lg
            hover:bg-blue-700
            transition
            disabled:opacity-50
            disabled:cursor-not-allowed
            shrink-0
            cursor-pointer
          "
        >
          <Send size={16} />
        </button>

      </div>

    </div>
  );
}