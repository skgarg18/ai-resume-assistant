"use client";


import { useState, useEffect } from "react";
import Navbar from "@/components/navbar/navbar"
import ChatBot from "@/components/chatbot/chatbot"
import Top_resume_list from "@/components/dashboard_panels/top_resume_list"
import ResumeDetails from "@/components/dashboard_panels/resume_details"
import HistoryPanel from "@/components/history_panel/history_panel";
import { useRouter } from "next/navigation";
import api from "@/lib/axios";



export default function ResultsDisplay() {

  const API_URL = "http://127.0.0.1:8000";

  const router = useRouter();

  const [results, setResults] = useState<any>([])
  const [names, setNames] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const [loading, setLoading] = useState(false);

  // New states for dashboard UI
  const [selectedCandidate, setSelectedCandidate] = useState<any | null>(null);

  const [sessionID, setSessionID] = useState<string>("")

  useEffect(() => {
    const session_id = sessionStorage.getItem("session_id");

    if (session_id) {
      setSessionID(session_id)
    }

    else {
      alert(`There is no session ID `)
      router.push("/")
    }

  }, [])


  const loadData = async () => {

    try {

      setLoading(true)

      const res = await api.get(
        `/api/session/${sessionID}`
      );

      const fetchedResults = res.data.results;

      setResults(fetchedResults);

      // console.log(fetchedResults)

      setNames(
        fetchedResults.map(
          (candidate: any) => candidate.name
        )
      );

      setSelectedCandidate(fetchedResults[0])

    } catch (error) {

      console.log(error);

      alert("There is some error IN GET api");

      router.push("/");
    }
    finally {
      setLoading(false)
    }
  };


  useEffect(() => {

    if (sessionID != "") { loadData(); }

  }, [sessionID]);


  if (loading) {
  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-gray-50">

      <div
        className="
          h-12 w-12
          border-4
          border-gray-200
          border-t-indigo-600
          rounded-full
          animate-spin
        "
      />

      <p className="mt-4 text-gray-500">
        Loading screening results...
      </p>

    </div>
  );
}




  return (

    <>

      <HistoryPanel
        showHistory={showHistory}
        setShowHistory={setShowHistory}
        currentSessionId={sessionID}
      />

      < main className="h-screen w-full bg-gray-50 flex flex-col font-sans text-gray-900 overflow-hidden">

      <Navbar variant="session" setShowHistory={setShowHistory} sessionId={sessionID}/>

      <div className="flex flex-1 overflow-auto">
        {/* LEFT COLUMN: Candidates List */}

        <div className="w-1/5 h-full overflow-auto">
          <Top_resume_list results={results} selectedCandidate={selectedCandidate} setSelectedCandidate={setSelectedCandidate} />
        </ div>

        {/* CENTER COLUMN: Resume PDF Viewer */}
        <main className="w-3/6 p-6 overflow-hidden flex flex-col bg-gray-50">
          {selectedCandidate ? (

            <ResumeDetails selectedCandidate={selectedCandidate} />

          ) : (
            <div className="h-full flex items-center justify-center text-gray-400">
              Select a candidate to view their resume
            </div>
          )}
        </main>

        {/* RIGHT COLUMN: AI Chatbot Side Panel */}
        <aside className="w-2/6 border-l bg-white flex flex-col shrink-0">
          <ChatBot results={results} names={names} sessionID={sessionID} setSelectedCandidate={setSelectedCandidate} />
        </aside>
      </div >
        </ main >
    </>
  )
}