"use client";

import { Loader2, Clock3 } from "lucide-react";

interface ProcessingCardProps {
  sessionId: string;
  setShowHistory: React.Dispatch<React.SetStateAction<boolean>>;
}

import Navbar from "../navbar/navbar";

export default function ProcessingCard({
  sessionId,
  setShowHistory
}: ProcessingCardProps) {
  return (


        <div className="flex-1 overflow-y-auto p-8 flex justify-center items-start">
      <div
        className="
          bg-white
          p-10
          rounded-xl
          shadow-lg
          border
          border-gray-200
          w-full
          max-w-2xl
          mt-10
          text-center
        "
      >
        <div className="flex justify-center">
          <Loader2
            size={56}
            className="text-blue-600 animate-spin"
          />
        </div>

        <h1 className="mt-6 text-3xl font-bold text-gray-800">
          Screening Started
        </h1>

        <p className="mt-3 text-gray-600">
          Your resumes are currently being processed in the background.
        </p>

        <p className="text-gray-600">
          This may take a few minutes depending on the number of resumes.
        </p>

        <div
          className="
            mt-8
            rounded-xl
            border
            border-blue-200
            bg-blue-50
            p-5
          "
        >
          <div className="flex items-center justify-center gap-2 text-blue-700 font-semibold">
            <Clock3 size={18} />
            Processing
          </div>

          <p className="mt-3 text-sm text-gray-600">
            You can safely leave this page. Your screening will continue in the
            background.
          </p>
        </div>

        <div
          className="
            mt-8
            rounded-lg
            border
            border-gray-200
            bg-gray-50
            p-4
          "
        >
          <p className="text-xs uppercase tracking-wide text-gray-500">
            Session ID
          </p>

          <p
            className="
              mt-2
              font-mono
              text-sm
              break-all
              text-gray-800
            "
          >
            {sessionId}
          </p>
        </div>

        <div className="mt-8 text-sm text-gray-500">
          You'll be notified once the screening has finished.
        </div>
      </div>
        </div>


  );
}