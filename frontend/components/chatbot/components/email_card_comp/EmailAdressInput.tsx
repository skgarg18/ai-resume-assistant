"use client";

import { useState, KeyboardEvent } from "react";
import { X } from "lucide-react";

interface EmailAddressInputProps {
  label: string;
  placeholder: string;
  emails: string[];
  setEmails: React.Dispatch<React.SetStateAction<string[]>>;
}

export default function EmailAddressInput({
  label,
  placeholder,
  emails,
  setEmails,
}: EmailAddressInputProps) {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const addEmail = () => {
    const email = input.trim().toLowerCase();

    if (!email) return;

    if (!emailRegex.test(email)) {
      setError("Invalid email address");
      return;
    }

    if (emails.includes(email)) {
      setError("Email already added");
      return;
    }

    setEmails((prev) => [...prev, email]);
    setInput("");
    setError("");
  };

  const removeEmail = (email: string) => {
    setEmails((prev) => prev.filter((e) => e !== email));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addEmail();
    }

    if (e.key === "Backspace" && input === "" && emails.length > 0) {
      removeEmail(emails[emails.length - 1]);
    }
  };

  return (
    <div className="flex flex-col gap-1 w-full min-w-0">
      <div className="flex items-center gap-3 w-full min-w-0">
        <label className="w-12 shrink-0 text-xs font-semibold text-gray-600">
          {label}
        </label>

        <div className="flex-1 min-w-0 min-h-8.5 rounded-lg border border-gray-200 bg-white px-2.5 py-1 shadow-xs flex flex-wrap items-center gap-1.5 transition focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 max-w-full overflow-hidden">
          {(emails ?? []).map((email) => (
            <div
              key={email}
              className="flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-md border border-blue-100 max-w-full truncate"
            >
              <span className="truncate">{email}</span>
              <button
                type="button"
                onClick={() => removeEmail(email)}
                className="hover:text-blue-900 transition shrink-0"
              >
                <X size={12} />
              </button>
            </div>
          ))}

          <input
            type="email"
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              if (error) setError("");
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="flex-1 min-w-30 outline-none text-xs text-gray-800 bg-transparent py-0.5"
          />
        </div>
      </div>

      {error && <p className="text-xs text-red-600 pl-15">{error}</p>}
    </div>
  );
}