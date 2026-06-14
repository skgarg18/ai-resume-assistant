"use client";

import { useState } from "react";
import { UserCheck, Loader2, CheckCircle2, UploadCloud } from "lucide-react"
import axios from "axios";

import { useRouter } from "next/navigation";




export default function Upload() {

  const API_URL = "http://127.0.0.1:8000";

  const router = useRouter();

  const [jd, setJd] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);

  // --- EVENT HANDLERS ---
  const handleScreening = async (e: React.SyntheticEvent<HTMLFormElement>) => {

    e.preventDefault();

    //  Return error if any of required field is missing
    if (!jd || !files) return alert("Please provide a JD and upload resumes.");

    // Setting loader
    setLoading(true);


    const formData = new FormData();
    formData.append("jd", jd);
    Array.from(files).forEach((file) => formData.append("files", file));

    try {
      const res = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      sessionStorage.setItem("session_id" , res.data.session_id)

      router.push(`/${res.data.session_id}/`)
    } catch (error) {
      console.error(error);
      alert("Error processing resumes.");
    }
    finally{
    setLoading(false);}
  };


  return (
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
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 hover:bg-blue-700 disabled:opacity-50 transition cursor-pointer"
          >
            {loading ? <Loader2 className="animate-spin" /> : <UploadCloud />}
            {loading ? "Analyzing Candidates..." : "Screen Resumes"}
          </button>
        </form>
      </div>
    </div>
  )
}