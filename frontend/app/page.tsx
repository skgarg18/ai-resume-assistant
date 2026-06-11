// This tells Next.js that this component runs in the browser (client-side), 
// which is required because we are using interactive hooks like useState.
"use client";

import { useState } from "react";
import axios from "axios";
import { Loader2, UploadCloud, UserCheck, Search, Plus, FileText, CheckCircle2 } from "lucide-react";
import ChatBot from "@/app/chatbot"; // Adjust path as necessary

export default function Home() {
  const API_URL = "http://127.0.0.1:8555";

  // --- STATE MANAGEMENT ---
  const [jd, setJd] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [names, setNames] = useState<string[]>([]);
  
  // New states for dashboard UI
  const [selectedCandidate, setSelectedCandidate] = useState<any | null>(null);
  const [pdfUrls, setPdfUrls] = useState<{ [key: string]: string }>({});

  // --- EVENT HANDLERS ---
  const handleScreening = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jd || !files) return alert("Please provide a JD and upload resumes.");

    setLoading(true);

    // Create local object URLs to display the original PDFs in the central iframe
    const urls: { [key: string]: string } = {};
    Array.from(files).forEach((file) => {
      urls[file.name] = URL.createObjectURL(file);
    });
    setPdfUrls(urls);

    const formData = new FormData();
    formData.append("jd", jd);
    Array.from(files).forEach((file) => formData.append("files", file));

    try {
      const res = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      setResults(res.data.shortlist);
      setNames(res.data.candidate_names);
      
      // Auto-select the first candidate when results come in
      if (res.data.shortlist && res.data.shortlist.length > 0) {
        setSelectedCandidate(res.data.shortlist[0]);
      }
    } catch (error) {
      console.error(error);
      alert("Error processing resumes.");
    }
    setLoading(false);
  };

  const resetDashboard = () => {
    setResults([]);
    setNames([]);
    setSelectedCandidate(null);
    setFiles(null);
    setJd("");
  };

  return (
    <main className="h-screen w-full bg-gray-50 flex flex-col font-sans text-gray-900 overflow-hidden">
      
      {/* --- TOP NAVBAR --- */}
      <nav className="h-16 bg-white border-b px-6 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 text-blue-600 font-bold text-xl">
          <FileText className="fill-blue-600 text-white" size={24} />
          ResumeAI
        </div>

        <div className="flex items-center gap-4">
          {results.length > 0 && (
            <button 
              onClick={resetDashboard}
              className="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
            >
              <Plus size={16} /> New Chat
            </button>
          )}
          <div className="flex items-center gap-3 border-l pl-4">
            <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
              R
            </div>
            <div className="text-sm">
              <p className="font-semibold leading-none">Recruiter</p>
              <p className="text-xs text-gray-500">Admin</p>
            </div>
          </div>
        </div>
      </nav>

      {/* --- MAIN DASHBOARD LAYOUT --- */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* State 1: Upload Form (Shows when no results exist) */}
        {results.length === 0 ? (
          <div className="flex-1 overflow-y-auto p-8 flex justify-center items-start">
            <div className="bg-white p-8 rounded-xl shadow-sm border w-full max-w-2xl mt-10">
              <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3 mb-6">
                <UserCheck className="text-blue-600" size={32} /> Start Screening
              </h1>
              <form onSubmit={handleScreening} className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold mb-2">Job Description</label>
                  <textarea
                    className="w-full border border-gray-300 p-4 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    rows={6}
                    placeholder="Paste the target Job Description here..."
                    value={jd}
                    onChange={(e) => setJd(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2">Upload Resumes (PDF)</label>
                  <input
                    type="file"
                    id='resume-upload'
                    multiple
                    accept="application/pdf"
                    className="hidden"
                    onChange={(e) => setFiles(e.target.files)}
                  />
                  <div className="flex items-center gap-4">
                    <label
                      htmlFor="resume-upload"
                      className="cursor-pointer px-5 py-2.5 bg-gray-100 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition"
                    >
                      Browse Files
                    </label>
                    <span className="text-sm text-gray-500">
                      {files ? `${files.length} file(s) selected` : "No files selected"}
                    </span>
                  </div>

                  {files && files.length > 0 && (
                    <ul className="mt-4 text-sm text-gray-600 max-h-32 overflow-y-auto bg-gray-50 p-3 rounded-lg border">
                      {Array.from(files).map((file, index) => (
                        <li key={index} className="flex items-center gap-2 mb-1">
                          <CheckCircle2 size={14} className="text-green-500" /> {file.name}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 hover:bg-blue-700 disabled:opacity-50 transition"
                >
                  {loading ? <Loader2 className="animate-spin" /> : <UploadCloud />}
                  {loading ? "Analyzing Candidates..." : "Screen Resumes"}
                </button>
              </form>
            </div>
          </div>
        ) : (
          /* State 2: Dashboard View (Shows when results exist) */
          <>
            {/* LEFT COLUMN: Candidates List */}
            <aside className="w-80 bg-white border-r flex flex-col shrink-0">
              <div className="p-4 border-b">
                <h2 className="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">Candidates</h2>
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 text-gray-400" size={16} />
                  <input 
                    type="text" 
                    placeholder="Search candidates..." 
                    className="w-full pl-9 pr-3 py-2 bg-gray-50 border rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-gray-50">
                {results.map((candidate) => (
                  <div 
                    key={candidate.id} 
                    onClick={() => setSelectedCandidate(candidate)}
                    className={`p-4 border rounded-xl cursor-pointer transition-all ${selectedCandidate?.id === candidate.id ? 'border-blue-500 bg-white shadow-sm ring-1 ring-blue-500' : 'bg-white border-gray-200 hover:border-blue-300'}`}
                  >
                    <div className="flex gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold shrink-0">
                        {candidate.filename.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start mb-1">
                          <h3 className="font-bold text-sm truncate text-gray-900">{candidate.filename}</h3>
                        </div>
                        <p className="text-xs text-gray-500 mb-2 truncate">Candidate Match Score</p>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 h-1.5 rounded-full overflow-hidden">
                            <div 
                              className="bg-green-500 h-full rounded-full" 
                              style={{ width: `${candidate.evaluation?.match_score || 0}%` }} 
                            />
                          </div>
                          <span className="text-xs font-bold text-green-600">
                            {candidate.evaluation?.match_score || 0}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </aside>

            {/* CENTER COLUMN: Resume PDF Viewer */}
            <main className="flex-1 p-6 overflow-hidden flex flex-col bg-gray-50">
              {selectedCandidate ? (
                <div className="bg-white rounded-xl border shadow-sm flex flex-col h-full overflow-hidden">
                  <div className="p-4 border-b flex justify-between items-center bg-white shrink-0">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedCandidate.filename}</h2>
                      <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                        Original Uploaded Resume
                      </p>
                    </div>
                    <div className="bg-green-50 px-4 py-2 rounded-lg border border-green-100 flex flex-col items-center">
                      <span className="text-xs text-green-700 font-bold uppercase">Match Score</span>
                      <span className="text-xl font-black text-green-600 leading-none">
                        {selectedCandidate.evaluation?.match_score || 0}%
                      </span>
                    </div>
                  </div>
                  
                  {/* Dynamic PDF Embed */}
                  <div className="flex-1 bg-gray-100 w-full relative">
                    {pdfUrls[selectedCandidate.filename] ? (
                      <iframe 
                        src={`${pdfUrls[selectedCandidate.filename]}#toolbar=0&view=FitH`} 
                        className="w-full h-full absolute inset-0"
                        title={`Resume of ${selectedCandidate.filename}`}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        Preview not available
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  Select a candidate to view their resume
                </div>
              )}
            </main>

            {/* RIGHT COLUMN: AI Chatbot Side Panel */}
            <aside className="w-[550px] border-l bg-white flex flex-col shrink-0">
              <ChatBot names={names} />
            </aside>
          </>
        )}
      </div>
    </main>
  );
}