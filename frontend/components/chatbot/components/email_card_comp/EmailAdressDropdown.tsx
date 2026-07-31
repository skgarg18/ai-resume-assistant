"use client";

import { EmailCandidate } from "../../types/chat";

interface EmailAdressDropdownProps {
  email_candidates: EmailCandidate[];
  selected_email_Candidate: EmailCandidate;
  setSelectedCandidate: (candidate: EmailCandidate) => void;
}

export default function EmailAdressDropdown({
  email_candidates,
  selected_email_Candidate,
  setSelectedCandidate,
}: EmailAdressDropdownProps) {
  return (
    <div className="flex items-center gap-3 w-full min-w-0">
      <label className="w-12 shrink-0 text-xs font-semibold text-gray-600">
        To
      </label>

      <select
        value={selected_email_Candidate?.email || ""}
        onChange={(e) => {
          const candidate = email_candidates.find((c) => c.email === e.target.value);
          if (candidate) {
            setSelectedCandidate(candidate);
          }
        }}
        className="flex-1 min-w-0 w-full truncate rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-xs text-gray-800 shadow-xs transition outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
      >
        {(email_candidates || []).map((candidate, index) => (
          <option
            key={candidate.resume_id || candidate.email || index}
            value={candidate.email}
          >
            {candidate.name} ({candidate.email})
          </option>
        ))}
      </select>
    </div>
  );
}