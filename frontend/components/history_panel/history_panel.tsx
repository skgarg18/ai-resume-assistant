"use client";

import axios from "axios";
import { useEffect, useState , useRef } from "react";

import { Trash2 ,
    LoaderCircle } from "lucide-react";

import { useRouter } from "next/navigation";

// Define the structure of a session object
interface Session {
    session_id: string;
    session_name: string;
    created_at: string;
}

// Define the props for the HistoryPanel components
interface Props {
    showHistory: boolean;
    setShowHistory: React.Dispatch<React.SetStateAction<boolean>>;
    currentSessionId?: string;
}


export default function HistoryPanel({
    showHistory,
    setShowHistory,
    currentSessionId
}: Props) {

    const router = useRouter();

    const API_URL = "http://127.0.0.1:8000";

    const [sessions, setSessions] = useState<Session[]>([]);

    const [deletingSessionId, setDeletingSessionId] =useState<string | null>(null);

    const activeSessionRef = useRef<HTMLDivElement | null>(null);

    // Load sessions from the backend when the component mounts or when showHistory changes
    useEffect(() => {
        if (!showHistory) return;

        const loadSessions = async () => {
            try {
                const res = await axios.get(
                    `${API_URL}/api/sessions`
                );

                setSessions(res.data);
            } catch (err) {
                console.log(err);
            }
        };

        loadSessions();
    }, [showHistory]);


    // Scroll to the active session when the history panel is shown
    useEffect(() => {

        if (
            showHistory &&
            activeSessionRef.current
        ) {

            activeSessionRef.current.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });

        }

    }, [showHistory]);


    // Load a specific session into the app
    const loadSession = (sessionId: string) => {
        sessionStorage.setItem(
            "session_id",
            sessionId
        );

        setShowHistory(false);

        router.push(`/${sessionId}`)
    };


    // Delete a specific session from the backend and update the state
    const handleDeleteSession = async (
        sessionID: string
    ) => {

        try {

            setDeletingSessionId(sessionID);

            await axios.delete(
                `${API_URL}/api/sessions/delete/${sessionID}`
            );

            setSessions((prev) =>
                prev.filter(
                    (session) =>
                        session.session_id !== sessionID
                )
            );

            if (sessionID === currentSessionId) {
                router.push("/");
            }


        } catch (error) {

            console.error(
                "Failed to delete session:",
                error
            );

        }
    };



    return (
        <div className="overflow-hidden">
            {/* Overlay */}

            <div
                onClick={() => setShowHistory(false)}
                className={`
                    fixed inset-0
                    bg-black/20
                    backdrop-blur-[2px]
                    z-40
                    transition-all duration-300

                    ${showHistory
                                ? "opacity-100"
                                : "opacity-0 pointer-events-none"
                            }
                `}
            />

            {/* Panel */}

            <div
                className={`
                    fixed right-1 top-20
                    h-[calc(100vh-6rem)]
                    w-105

                    flex flex-col

                    bg-white
                    border border-gray-200
                    rounded-2xl

                    shadow-[0_0_40px_rgba(0,0,0,0.12)]

                    z-50

                    transition-transform duration-300 ease-out

                    ${showHistory
                                ? "translate-x-0"
                                : "translate-x-full"
                            }
                `}
            >

                {/* Header */}

                <div className="sticky top-0 z-10 bg-white border-b border-gray-200 rounded-2xl">

                    <div className="flex items-center justify-between px-5 py-4">

                        <div>
                            <h2 className="uppercase text-lg font-semibold text-gray-800">
                                Screening History
                            </h2>

                            <p className="text-sm text-gray-500">
                                Previous screening sessions
                            </p>
                        </div>

                        <button
                            onClick={() => setShowHistory(false)}
                            className="
                                h-8 w-8
                                rounded-lg
                                hover:bg-gray-100
                                transition-colors
                                text-gray-500
                                cursor-pointer
                            "
                            >
                            ✕
                        </button>

                    </div>

                </div>

                {/* Content */}

                {
                    sessions.length === 0 ? (

                        <div className="h-full flex flex-col items-center justify-center text-center px-6">

                            <div className="text-5xl mb-4">
                                📋
                            </div>

                            <div className="font-medium text-gray-700">
                                No Screening History
                            </div>

                            <div className="text-sm text-gray-500 mt-2">
                                Your previous screening sessions will appear here.
                            </div>

                        </div>

                    ) : (

                        <div className="flex flex-col gap-2 overflow-y-auto h-full pb my-3">

                            {sessions.map((session) => {

                               const isCurrent =
                                   session.session_id === currentSessionId;

                                const isDeleting =
                                        deletingSessionId === session.session_id;

                               return (

                                   <div
                                       key={session.session_id}
                                       ref={
                                            isCurrent
                                                ? activeSessionRef
                                                : null
                                        }
                                       className={`
                                           group
                                           mx-2

                                           rounded-xl
                                           border

                                           transition-all duration-200

                                           ${isDeleting
                                                ? `
                                                    opacity-50
                                                    scale-[0.98]
                                                    pointer-events-none
                                                `
                                                : ""
                                            }

                                           ${isCurrent
                                               ? `
                                                   bg-indigo-50
                                                   border-indigo-300
                                                   shadow-sm
                                               `
                                               : `
                                                   border-gray-200
                                                   hover:bg-slate-50
                                                   hover:border-slate-300
                                               `
                                           }
                                       `}
                                   >

                                       <div className="flex items-center">
                                       
                                           {/* SESSION BUTTON */}
                                       
                                           <button
                                               disabled={isCurrent}
                                               onClick={() =>
                                                   loadSession(session.session_id)
                                               }
                                               className={`
                                                   flex-1
                                                   min-w-0

                                                   p-2

                                                   text-left

                                                   ${isCurrent
                                                       ? "cursor-default"
                                                       : "cursor-pointer"
                                                   }
                                               `}
                                           >

                                               <div className="flex items-start justify-between gap-2">
                                               
                                                   <div className="flex-1 min-w-0">
                                               
                                                       <div
                                                           className={`
                                                               font-medium
                                                               text-sm
                                                               leading-5

                                                               truncate

                                                               ${isCurrent
                                                                   ? "text-indigo-900"
                                                                   : "text-gray-700"
                                                               }
                                                           `}
                                                       >
                                                           {session.session_name}
                                                       </div>
                                                           
                                                       <div className="text-xs text-gray-400 mt-1">
                                                           {new Date(
                                                               session.created_at
                                                           ).toLocaleDateString()}
                                                       </div>
                                                       
                                                   </div>
                                                       
                                                   {isCurrent && (

                                                       <span
                                                           className="
                                                               bg-indigo-100
                                                               text-indigo-700

                                                               text-[11px]
                                                               font-medium

                                                               px-2.5
                                                               py-1

                                                               rounded-full

                                                               shrink-0
                                                           "
                                                       >
                                                           Active
                                                       </span>

                                                   )}

                                               </div>
                                               
                                           </button>
                                               
                                               
                                           {/* DELETE BUTTON */}

                                           {!isCurrent && (
                                               
                                           <button
                                               onClick={() =>
                                                   handleDeleteSession(
                                                       session.session_id
                                                   )
                                               }
                                               className="
                                                   mr-2
                                                   p-2
                                           
                                                   rounded-lg
                                           
                                                   text-gray-400
                                           
                                                   opacity-50
                                                   group-hover:opacity-100
                                           
                                                   hover:text-red-500
                                                   hover:bg-red-50
                                           
                                                   transition-all duration-200
                                           
                                                   cursor-pointer
                                               "
                                               title="Delete session"
                                           >
                                               {isDeleting ? (
                                                    <LoaderCircle
                                                        size={16}
                                                        className="animate-spin"
                                                    />
                                                ) : (
                                                    <Trash2 size={16} />
                                                )}
                                           </button>
                                           )}
                                           
                                       </div>
                                           
                                   </div>

                               );
                            })}

                        </div>

                    )
                }

            </div>

        </div >
    );
}