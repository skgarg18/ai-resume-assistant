import { CandidateComparisonData } from "../../types/chat";

interface Props {
  data: CandidateComparisonData;
}

export default function CandidateComparison({ data }: Props) {
  const candidate1 = data?.candidates?.[0] || "Candidate 1";
  const candidate2 = data?.candidates?.[1] || "Candidate 2";
  const comparisonSections = data?.comparison || (data as any)?.comparison_cards || [];

  return (
    <div className="space-y-3 text-xs w-full max-w-full">
      
      {/* 1. Summary Header Banner */}
      {data?.summary && (
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 leading-relaxed">
          <span className="font-semibold text-slate-900">Summary: </span>
          {data.summary}
        </div>
      )}

      {/* 2. Recommendation Banner */}
      {data?.recommendation && (
        <div className="p-2.5 bg-emerald-50/80 border border-emerald-200 rounded-lg text-emerald-950">
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-[9px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100/90 px-1.5 py-0.5 rounded border border-emerald-200">
              RECOMMENDED
            </span>
            <span className="font-bold text-emerald-900 text-xs">
              {data.winner || "No clear winner"}
            </span>
          </div>
          <p className="text-emerald-900/90 leading-relaxed">
            {data.recommendation}
          </p>
        </div>
      )}

      {/* 3. Sticky Column Header for Candidates */}
      <div className="grid grid-cols-2 gap-2 font-semibold text-slate-900 px-2 py-1 bg-slate-100/80 border border-slate-200 rounded-md">
        <div className="truncate">{candidate1}</div>
        <div className="truncate">{candidate2}</div>
      </div>

      {/* 4. Strengths Section */}
      {(data?.strengths_candidate_1?.length > 0 || data?.strengths_candidate_2?.length > 0) && (
        <div className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm">
          <div className="bg-slate-100/70 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-600 border-b border-slate-200">
            Key Strengths
          </div>
          <div className="grid grid-cols-2 divide-x divide-slate-200 p-2 gap-2">
            <ul className="list-disc pl-3 space-y-1 text-slate-700">
              {data.strengths_candidate_1?.map((s, i) => (
                <li key={i} className="leading-snug">{s}</li>
              ))}
            </ul>
            <ul className="list-disc pl-3 space-y-1 text-slate-700">
              {data.strengths_candidate_2?.map((s, i) => (
                <li key={i} className="leading-snug">{s}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* 5. Sectional Comparison Strips */}
      <div className="space-y-2">
        {comparisonSections.map((item: any, index: number) => (
          <div key={index} className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm">
            {/* Aspect Header Banner */}
            <div className="bg-slate-100/70 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-700 border-b border-slate-200">
              {item.title}
            </div>
            {/* Split Comparison Columns */}
            <div className="grid grid-cols-2 divide-x divide-slate-200 p-2 gap-2 text-slate-700 leading-normal whitespace-pre-line break-words">
              <div>{item.candidate_1}</div>
              <div>{item.candidate_2}</div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}