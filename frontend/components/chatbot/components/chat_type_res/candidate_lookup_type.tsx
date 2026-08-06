import React, { useMemo } from "react";
import ReactMarkdown from "react-markdown"; // Optional: handles **bold** formatting inside points

import {CandidateLookupResult} from "../../types/chat"

interface Props {
  candidates: CandidateLookupResult[];
  missingNames: string[];
  results: any[];
  setSelectedCandidate: React.Dispatch<React.SetStateAction<any | null>>;
}

export default function CandidateLookupMessage({
  candidates,
  missingNames,
  results,
  setSelectedCandidate,
}: Props) {
  const candidateMap = useMemo(
    () =>
      Object.fromEntries(
        results.map((candidate) => [candidate.resume_id, candidate])
      ),
    [results]
  );

  return (
    <div className="text-sm">
      {candidates.map((candidate, index) => {
        const fullCandidate = candidateMap[candidate.resume_id];

        if (!fullCandidate) return null;

        // Safely normalize bullet points to array format
        const pointsList: string[] = Array.isArray(candidate.bullet_points)
          ? candidate.bullet_points
          : typeof candidate.bullet_points === "string"
          ? (candidate.bullet_points as string)
              .split("\n")
              .map((pt) => pt.replace(/^[-\*\s]+/, "").trim())
              .filter(Boolean)
          : [];

        return (
          <div key={candidate.resume_id}>
            <div className="space-y-1.5">
              {/* Candidate Header without numbering */}
              <div className="text-base">
                <button
                  onClick={() => setSelectedCandidate(fullCandidate)}
                  className="font-bold text-sm text-slate-900 hover:text-blue-600 hover:underline transition cursor-pointer"
                >
                  {fullCandidate.name}
                </button>

                <span className="ml-1.5 font-normal text-slate-600 text-xs">
                  (Match Score:{" "}
                  <strong className="font-semibold text-xs text-slate-900">
                    {fullCandidate.overall_score}
                  </strong>
                  )
                </span>
              </div>

              {/* Bullet Points with proper left-hanging indent */}
              <ul className="list-disc text-xs pl-5 space-y-2 leading-relaxed text-slate-700">
                {pointsList.map((point, ptIdx) => (
                  <li key={ptIdx} className="pl-0.5">
                    <ReactMarkdown components={{ p: "span" }}>
                      {point}
                    </ReactMarkdown>
                  </li>
                ))}
              </ul>
            </div>

            {/* Horizontal Line Separator (Only rendered between candidates) */}
            {index < candidates.length - 1 && (
              <hr className="my-5 border-t border-slate-200" />
            )}
          </div>
        );
      })}

      {/* Missing Candidates Alert */}
      {missingNames && missingNames.length > 0 && (
        <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-3.5 text-xs text-amber-800">
          <div className="font-semibold mb-1">Candidates Not Found</div>
          <div>{missingNames.join(", ")}</div>
        </div>
      )}
    </div>
  );
}