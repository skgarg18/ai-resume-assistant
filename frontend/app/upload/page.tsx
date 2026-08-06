"use client";

import { Suspense, useState } from "react";
import Navbar from "../../components/navbar/navbar";
import Upload from "../../components/details_upload/upload";
import HistoryPanel from "@/components/history_panel/history_panel";

export default function Home() {
  const [showHistory, setShowHistory] = useState(false);

  return (
    <>
      <HistoryPanel
        showHistory={showHistory}
        setShowHistory={setShowHistory}
      />

      <main className="h-screen w-full bg-gray-50 flex flex-col font-sans text-gray-900 overflow-hidden">

        <Navbar
          variant="home"
          setShowHistory={setShowHistory}
        />

        <div className="flex-1 flex overflow-hidden">

          <Suspense fallback={<div>Loading...</div>}>
            <Upload />
          </Suspense>

        </div>
      </main>
    </>
  );
}