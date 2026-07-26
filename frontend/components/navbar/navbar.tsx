"use client";

import Link from "next/link";
import { FileText, Plus, History } from "lucide-react"
import { useRouter } from "next/navigation";

import { removeToken , isAuthenticated} from "../../lib/auth"

import { useEffect, useState } from "react";


interface NavbarProps {
  variant: "home" | "session";
  setShowHistory: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function Navbar({ variant, setShowHistory }: NavbarProps) {
  const router = useRouter();

  const resetDashboard = () => {

    sessionStorage.clear();
    router.push("/")
  }

  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
      setLoggedIn(isAuthenticated());
  }, []);

  const handleLogout = () => {
      removeToken();
      setLoggedIn(false);
      router.replace("/login");
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

        {variant === "session" &&

          <div className="flex items-center gap-4">
            <button
              onClick={resetDashboard}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors cursor-pointer"
            >
              <Plus size={16} /> New Chat
            </button>
          </div>
        }
          

          <div className="flex items-center gap-4">

            {loggedIn ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
            >
              Log Out
            </button>
            ):
            (

              <button
              onClick={removeToken}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
            >

              <Link href="/login">
                    Login
              </Link>
              
            </button>

            )
          }
          </div>

      </div>
    </nav>

  )

}