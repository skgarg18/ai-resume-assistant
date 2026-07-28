"use client";

import Link from "next/link";
import { FileText, Plus, History, Download, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import api from "@/lib/axios";
import { removeToken, isAuthenticated } from "../../lib/auth";

interface NavbarProps {
  variant: "home" | "session";
  setShowHistory: React.Dispatch<React.SetStateAction<boolean>>;
  sessionId?: string; // Optional session ID input
}

export default function Navbar({ variant, setShowHistory, sessionId }: NavbarProps) {
  const router = useRouter();

  const resetDashboard = () => {
    sessionStorage.clear();
    router.push("/");
  };

  const [loggedIn, setLoggedIn] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    setLoggedIn(isAuthenticated());
  }, []);

  const handleLogout = () => {
    removeToken();
    setLoggedIn(false);
    router.replace("/login");
  };

  /**
   * Triggers the backend export route via the custom Axios instance with Bearer auth.
   */
  const handleDownloadResults = async () => {
    // Fallback to sessionStorage if sessionId prop was not explicitly passed
    const activeSessionId = sessionId || sessionStorage.getItem("session_id");

    if (!activeSessionId) {
      alert("Session ID missing. Cannot download evaluation report.");
      return;
    }

    try {
      setIsDownloading(true);

      // Make API call via Axios instance with blob responseType
      const response = await api.get(`/api/session/${activeSessionId}/export`, {
        responseType: "blob",
      });

      // Create blob object from Axios response payload
      const blob = new Blob([response.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const downloadUrl = window.URL.createObjectURL(blob);

      // Parse filename from Content-Disposition header if available
      const contentDisposition = response.headers["content-disposition"];
      let filename = `Resume_Evaluation_Report_${activeSessionId}.xlsx`;

      if (contentDisposition && contentDisposition.includes("filename*=UTF-8''")) {
        filename = decodeURIComponent(contentDisposition.split("filename*=UTF-8''")[1]);
      } else if (contentDisposition && contentDisposition.includes("filename=")) {
        filename = contentDisposition.split("filename=")[1].replace(/"/g, "");
      }

      // Trigger browser download anchor link
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // Cleanup DOM object
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Failed to download evaluation report:", error);
      alert("An error occurred while generating your Excel report. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <nav className="h-14 bg-white border-b border-gray-200 px-8 flex items-center justify-between shadow-sm shrink-0">
      <div className="flex items-center gap-2 text-blue-600 font-bold text-2xl tracking-tight">
        <FileText className="fill-blue-600 text-white" size={24} />
        ResumeAI
      </div>

      <div className="flex gap-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowHistory?.(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-500 bg-white text-sm font-medium text-gray-700 hover:bg-gray-100 hover:border-gray-300 transition-all duration-200 cursor-pointer"
          >
            <History size={16} /> History
          </button>
        </div>

        {variant === "session" && (
          <div className="flex items-center gap-3">
            {/* Download Results Button */}
            <button
              onClick={handleDownloadResults}
              disabled={isDownloading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-emerald-600 bg-emerald-50 text-emerald-700 text-sm font-medium hover:bg-emerald-100 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDownloading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Exporting...
                </>
              ) : (
                <>
                  <Download size={16} /> Download Results
                </>
              )}
            </button>

            {/* New Chat Button */}
            <button
              onClick={resetDashboard}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors cursor-pointer"
            >
              <Plus size={16} /> New Chat
            </button>
          </div>
        )}

        <div className="flex items-center gap-4">
          {loggedIn ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
            >
              Log Out
            </button>
          ) : (
            <button className="flex items-center gap-2 px-5 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors">
              <Link href="/login">Login</Link>
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}