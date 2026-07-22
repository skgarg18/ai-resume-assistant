// This tells Next.js that this component runs in the browser (client-side), 
// which is required because we are using interactive hooks like useState.
"use client";

import { useState } from 'react'
import Navbar from "../components/navbar/navbar";
import Upload from "../components/details_upload/upload"
import HistoryPanel from '@/components/history_panel/history_panel';


export default function Home() {

  const [showHistory, setShowHistory] = useState<boolean>(false)

  // --- STATE MANAGEMENT ---

  return (

    <>
      <HistoryPanel
        showHistory={showHistory}
        setShowHistory={setShowHistory}
      />

      <main className="h-screen w-full bg-gray-50 flex flex-col font-sans text-gray-900 overflow-hidden">

        {/* --- TOP NAVBAR --- */}
        <Navbar variant="home" setShowHistory={setShowHistory} />


        {/* --- MAIN DASHBOARD LAYOUT --- */}
        <div className="flex-1 flex overflow-hidden">

          {/* State 1: Upload Form (Shows when no results exist) */}

          <Upload setShowHistory={setShowHistory}/>

        </div>
      </main>
    </>
  );
}