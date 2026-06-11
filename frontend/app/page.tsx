// This tells Next.js that this component runs in the browser (client-side), 
// which is required because we are using interactive hooks like useState.
"use client";

import { useState } from "react";
import axios from "axios";
import { Loader2, UploadCloud, UserCheck, FileQuestion } from "lucide-react";
import ChatBot from "@/app/chatbot";


export default function Home() {
  // --- STATE MANAGEMENT (React Hooks) ---
  // useState holds data that, when changed, causes the UI to re-render.

  const API_URL = "http://127.0.0.1:8555"

  // Standard string state for the Job Description
  const [jd, setJd] = useState("");

  // TypeScript specific: We tell TS this will hold a 'FileList' object (from the browser) or 'null'
  const [files, setFiles] = useState<FileList | null>(null);

  // Boolean state for loading spinners
  const [loading, setLoading] = useState(false);

  // Array state to hold the results from the API. 'any[]' means an array of any object structure.
  const [results, setResults] = useState<any[]>([]);

  // Object states where the key is the resume ID (string) and the value is the questions (string) or loading status (boolean)
  const [activeQuestions, setActiveQuestions] = useState<{ [key: string]: string }>({});
  const [loadingQuestions, setLoadingQuestions] = useState<{ [key: string]: boolean }>({});

  // Ayyay to store names of top matched resumes
  const[names , setNames] = useState<string[]>([])
  // --- EVENT HANDLERS ---
  // React.FormEvent is a TypeScript type that knows this event comes from a form submission
  const handleScreening = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevents the page from refreshing on form submit
    if (!jd || !files) return alert("Please provide a JD and upload resumes.");

    setLoading(true);

    // FormData is a standard browser API used to send files over HTTP
    const formData = new FormData();
    formData.append("jd", jd);
    Array.from(files).forEach((file) => formData.append("files", file));

    try {
      const res = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResults(res.data.shortlist); // Save the API response into the 'results' state
      setNames(res.data.candidate_names);

    } catch (error) {
      console.error(error);
      alert("Error processing resumes.");
    }
    setLoading(false);
  };

  const handleGenerateQuestions = async (resume: any) => {
    setLoadingQuestions((prev) => ({ ...prev, [resume.id]: true }));
    try {
      const res = await axios.post(`${API_URL}/api/generate_questions`, {
        jd: jd,
        resume_text: resume.raw_text,
      });
      // Update the specific candidate's question state using their unique ID
      setActiveQuestions((prev) => ({ ...prev, [resume.id]: res.data.questions }));
    } catch (error) {
      console.error(error);
    }
    setLoadingQuestions((prev) => ({ ...prev, [resume.id]: false }));
  };

  // --- THE UI (TSX / JSX) ---
  // This looks like HTML, but it's actually compiled into JavaScript.
  return (
    // 'className' is used instead of HTML's 'class'. We are using Tailwind CSS classes here.
    <main className="min-h-screen bg-gray-50 p-8 text-gray-900">
      <div className="max-w-5xl mx-auto space-y-8">

        {/* Standard HTML tags work normally. Lucide icons are imported as React components like <UserCheck /> */}
        <h1 className="text-4xl font-bold text-blue-600 flex items-center gap-3">
          <UserCheck size={40} /> AI Resume Assistant
        </h1>

        <div className="bg-white p-6 rounded-xl shadow-sm border">
          {/* React binds the submit event to our handleScreening function */}
          <form onSubmit={handleScreening} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Job Description</label>
              <textarea
                className="w-full border p-3 rounded-lg"
                rows={5}
                placeholder="Paste the target Job Description here..."
                value={jd} // The text area is controlled by the 'jd' state
                onChange={(e) => setJd(e.target.value)} // Updates the state whenever the user types
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Upload Resumes (PDF)</label>
              <input
                type="file"
                id='resume-upload'
                multiple
                accept="application/pdf"
                className="hidden"
                onChange={(e) => setFiles(e.target.files)} // Grabs the files from the browser input
              />
              <label
                htmlFor="resume-upload"
                className="cursor-pointer px-4 py-2 bg-blue-500 text-white rounded-lg"
              >
                Upload Resumes
              </label>

              {files && files.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium">Selected Files:</p>

                  <ul className="mt-1 text-sm text-gray-600">
                    {Array.from(files).map((file, index) => (
                      <li key={index}>
                        📄 {file.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading} // Disables the button if 'loading' is true
              className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-blue-700 disabled:opacity-50"
            >
              {/* Using curly braces {} allows us to write JS logic inside HTML. 
                  Here, we show a spinning loader icon IF loading is true, otherwise the cloud icon */}
              {loading ? <Loader2 className="animate-spin" /> : <UploadCloud />}
              {loading ? "Analyzing Candidates..." : "Screen Resumes"}
            </button>
          </form>
        </div>

        {/* --- CONDITIONAL RENDERING --- */}
        {/* 'results.length > 0 && (...)' means: If there are results, render the following HTML block. */}
        {results.length > 0 && (

          <div className="space-y-8 ">

            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Top Matched Candidates</h2>

              {/* .map() is how you do loops in React HTML. For every candidate in the results array, we render a card. */}
              {results.map((candidate) => (
                // When rendering arrays, React needs a unique 'key' prop on the parent element
                <div key={candidate.id} className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      {/* Injecting variables into the HTML using {} */}
                      <h3 className="text-xl font-bold">{candidate.filename}</h3>
                      <p className="text-gray-600 mt-2">{candidate.evaluation.summary}</p>
                    </div>
                    <div className="bg-green-100 text-green-800 text-2xl font-bold px-4 py-2 rounded-full">
                      {candidate.evaluation.match_score}%
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm text-red-500">Missing Skills:</h4>
                    <div className="flex gap-2 flex-wrap mt-1">
                      {/* Looping through the nested array of missing skills */}
                      {candidate.evaluation.missing_skills.map((skill: string, i: number) => (
                        <span key={i} className="bg-red-50 text-red-600 text-xs px-2 py-1 rounded border border-red-100">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <button
                      onClick={() => handleGenerateQuestions(candidate)} // Trigger the API call for this specific candidate
                      className="text-blue-600 font-medium flex items-center gap-2 hover:underline"
                    >
                      <FileQuestion size={18} />
                      Generate Interview Questions
                    </button>

                    {/* Show a loader specifically for this candidate while their questions generate */}
                    {loadingQuestions[candidate.id] && <Loader2 className="animate-spin mt-4 text-blue-600" />}

                    {/* If questions exist for this candidate, render them here */}
                    {activeQuestions[candidate.id] && (
                      <div className="mt-4 p-4 bg-gray-50 rounded-lg whitespace-pre-wrap text-sm text-gray-800">
                        {activeQuestions[candidate.id]}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
            </div>

            <div className="">
              <ChatBot names = {names}/>
            </div>

          </div>
        )}
      </div>
    </main>
  );
}