"use client";


import { UserCheck, Loader2, CheckCircle2, UploadCloud, FileText, FolderOpen } from "lucide-react"
import { SiGoogledrive } from "react-icons/si";
import axios from "axios";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

import { useRouter } from "next/navigation";




export default function Upload() {

  const API_URL = "http://127.0.0.1:8000";

  const searchParams = useSearchParams(); 

  useEffect(() => {
    const connected =
      searchParams.get("google_connected");

    const userId =
        searchParams.get("user_id");

    // Restore only after OAuth redirect
    if (connected === "true") {

      const savedJD =
        sessionStorage.getItem("jd");

      const savedDriveLink =
        sessionStorage.getItem("drive_link");

      if (savedJD) {
        setJd(savedJD);
      }

      if (savedDriveLink) {
        setDriveLink(savedDriveLink);
      }

      setGoogleConnected(true);

      if (userId) {
        localStorage.setItem("user_id", userId);
      }

      // Cleanup after restoring
      sessionStorage.removeItem("jd");
      sessionStorage.removeItem("drive_link");
    }

  }, [searchParams]);


  const connectGoogle = () => {

    sessionStorage.setItem(
      "jd",
      jd
    );

    sessionStorage.setItem(
      "drive_link",
      driveLink
    );

    window.location.href =
      "http://localhost:8000/auth/google";
  };



  const [uploadMode, setUploadMode] =
    useState<"pdf" | "drive">("pdf");

  const [driveLink, setDriveLink] =
    useState("");

  const [googleConnected, setGoogleConnected] =
    useState(false);

  const router = useRouter();

  const [jd, setJd] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);

  // --- EVENT HANDLERS ---
  const handleScreening = async (e: React.SyntheticEvent<HTMLFormElement>) => {

    e.preventDefault();

    //  Return error if any of required field is missing
    if (!jd) {
      return alert(
        "Please provide a Job Description."
      );
    }

    if (
      uploadMode === "pdf" &&
      (!files || files.length === 0)
    ) {
      return alert(
        "Please upload resumes."
      );
    }

    if (
      uploadMode === "drive" &&
      !driveLink
    ) {
      return alert(
        "Please provide a Drive folder link."
      );
    }

    // Setting loader
    setLoading(true);


    const formData = new FormData();
    formData.append("jd", jd);

    const userId =
    localStorage.getItem("user_id");

    if (userId) {
        formData.append("user_id", userId);
    }

    if (uploadMode === "pdf" && files) {
      Array.from(files).forEach((file) => formData.append("files", file));
    }
    if (uploadMode === "drive") {
      formData.append(
        "drive_link",
        driveLink
      );
    }

    try {
      const res = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      sessionStorage.setItem("session_id", res.data.session_id)

      router.push(`/${res.data.session_id}/`)

      sessionStorage.removeItem("jd");
      sessionStorage.removeItem("drive_link");

      setJd("");
      setDriveLink("");
      setFiles(null);

    } catch (error) {
      console.error(error);
      alert("Error processing resumes.");
    }
    finally {
      setLoading(false);
    }
  };


  return (
    <div className="flex-1 overflow-y-auto p-8 flex justify-center items-start">

      <div className="
       bg-white p-8
       rounded-xl shadow-lg 
       border     border-gray-200
       backdrop-blur-sm w-full max-w-2xl mt-10">

        <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3 mb-6">
          <UserCheck className="text-blue-600" size={32} /> Start Screening
        </h1>
        <form onSubmit={handleScreening} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold mb-2">Job Description</label>
            <textarea
              className="w-full border border-gray-300 p-4 rounded-lg transition focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              rows={6}
              placeholder="Paste the target Job Description here..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              type="button"
              onClick={() => setUploadMode("pdf")}
              className={`
                  flex items-center justify-center gap-3
                  py-4 rounded-xl border-2
                  transition-all duration-200
                  cursor-pointer

                  ${uploadMode === "pdf"
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                }
                `}
            >
              <FileText size={22} />
              <div className="text-left">
                <p className="font-semibold">Upload Files</p>
                <p className="text-xs opacity-70">
                  Select resume files manually
                </p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setUploadMode("drive")}
              className={`
                  flex items-center justify-center gap-3
                  py-4 rounded-xl border-2
                  transition-all duration-200
                  cursor-pointer
                          
                  ${uploadMode === "drive"
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                }
                `}
            >
              <SiGoogledrive size={22} />
              <div className="text-left">
                <p className="font-semibold">Google Drive</p>
                <p className="text-xs opacity-70">
                  Import resumes from Drive
                </p>
              </div>
            </button>
          </div>

          {uploadMode === "pdf" && (

            <div className="">

              <div>
                <label className="block text-sm font-semibold mb-2">Upload Resumes (PDF, DOC)</label>
                <input
                  type="file"
                  id='resume-upload'
                  multiple
                  accept=".pdf,.docx"
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
                    <div className="flex flex-wrap gap-2 mt-4 overflow-auto max-h-40">

                        {Array.from(files).map(file => (
                        
                            <div
                                key={file.name}
                                className="
                                    flex items-center gap-2
                                    bg-blue-50
                                    border border-blue-200
                                    rounded-full
                                    px-3 py-1
                                    text-sm
                                "
                            >
                                <CheckCircle2
                                    size={14}
                                    className="text-green-600"
                                />

                                {file.name}
                        
                            </div>

                        ))}

                    </div>
                )}
              </div>



            </ div>

          )}



          {uploadMode === "drive" && (

            <div className="space-y-4">

              {googleConnected ? (

                <div
                  className="
                      border rounded-lg
                      p-3
                      bg-green-50
                    "
                >
                  <p className="font-medium text-green-700">
                    ✓ Google Drive Connected
                  </p>
                 
                </div>

              ) : (

                <button
                  type="button"
                  onClick={connectGoogle}
                  className="
                    w-full
                    py-3
                    rounded-xl
                    bg-[#4285F4]
                    text-white
                    font-medium
                    hover:bg-[#3367d6]
                    transition
                    flex
                    items-center
                    justify-center
                    gap-3
                    cursor-pointer
                    "
                >
                  Connect Google Drive
                </button>

              )}

              <input
                type="text"
                value={driveLink}
                disabled={!googleConnected}
                onChange={(e) =>
                  setDriveLink(e.target.value)
                }
                placeholder={
                  googleConnected
                    ? "Paste Drive folder link..."
                    : "Connect Google Drive first"
                }
                className="
                    w-full
                    px-3 py-2
                    border rounded-lg
                    disabled:bg-gray-100
                    disabled:text-gray-400
                  "
              />

            </div>

          )}

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