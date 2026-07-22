import React from "react";

interface RecruiterInsight {
  insight: string;
  category: string;
  evidence: string;
  importance: "High" | "Medium" | "Low";
}

interface RecruiterInsightsProps {
  insights: RecruiterInsight[];
}

const importanceStyles: Record<
  RecruiterInsight["importance"],
  string
> = {
  High: "bg-red-100 text-red-700 border-red-200",
  Medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  Low: "bg-green-100 text-green-700 border-green-200",
};

const RecruiterInsights: React.FC<RecruiterInsightsProps> = ({
  insights,
}) => {

  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <div className="">
      <h3 className="font-bold uppercase text-sm text-gray-800 mb-4">
          Key Insights
      </h3>

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <div
            key={index}
            className="rounded-lg border border-gray-200 bg-gray-50 p-4 transition-all duration-200 hover:border-blue-200 hover:bg-blue-50"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-gray-900">
                  {insight.insight}
                </h4>

                <span className="mt-1 inline-block rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-700">
                  {insight.category}
                </span>
              </div>

              <span
                className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                  importanceStyles[insight.importance]
                }`}
              >
                {insight.importance}
              </span>
            </div>

            <p className="mt-3 text-sm leading-relaxed text-gray-600">
              {insight.evidence}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecruiterInsights;