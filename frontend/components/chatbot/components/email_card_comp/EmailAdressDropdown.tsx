"use client";

interface EmailAdressDropdownProps {
  emailIds: string[];
  selectedEmail: string;
  setSelectedEmail: React.Dispatch<React.SetStateAction<string>>;
}

export default function EmailAdressDropdown({
  emailIds,
  selectedEmail,
  setSelectedEmail,
}: EmailAdressDropdownProps) {
  return (
    <div className="flex items-center gap-3">
      <label className="w-12 shrink-0 text-xs font-semibold text-gray-600">
        To
      </label>

      <select
        value={selectedEmail}
        onChange={(e) => setSelectedEmail(e.target.value)}
        className="flex-1 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-xs text-gray-800 shadow-xs transition outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
      >
        {emailIds.map((email, index) => (
          <option key={index} value={email}>
            {email}
          </option>
        ))}
      </select>
    </div>
  );
}