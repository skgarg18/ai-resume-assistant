import React, { useMemo } from "react";

import {CandidateSearchCandidate} from "../../types/chat"


interface Props {
  candidates: CandidateSearchCandidate[];
  results: any[];
  setSelectedCandidate: React.Dispatch<React.SetStateAction<any | null>>;
}

export default function CandidateSearchMessage({
  candidates,
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
    <div className="space-y-4 text-sm">
      <h3 className="font-semibold text-slate-800">
        Matching Candidates:
      </h3>

      {candidates.map((candidate, index) => {
        const fullCandidate = candidateMap[candidate.id];

        if (!fullCandidate) return null;

        return (
          <div key={candidate.id} className="pb-4 last:pb-0">
            <div className="flex items-start">
              <span className="w-6 shrink-0 font-semibold text-slate-700">
                {index + 1}.
              </span>

              <div className="flex-1">
                <div>
                  <button
                    onClick={() => setSelectedCandidate(fullCandidate)}
                    className="font-semibold text-slate-800 hover:text-blue-600 hover:underline transition cursor-pointer"
                  >
                    {fullCandidate.name}
                  </button>

                  <span className="text-slate-700">
                    {" "}
                    (Match Score:{" "}
                    <strong>{fullCandidate.overall_score}</strong>)
                  </span>
                </div>

                {candidate.match_significance && (
                  <p className="mt-1 text-slate-700 leading-relaxed">
                    {candidate.match_significance}
                  </p>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}