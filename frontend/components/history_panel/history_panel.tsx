"use client";


import api from "@/lib/axios";

import { useEffect, useState, useRef } from "react";

import {
    Trash2,
    LoaderCircle,
    User
} from "lucide-react";

import { useRouter } from "next/navigation";

import SessionCard from "./session_card";

// Define the structure of a session object
interface Session {
    session_id: string;
    session_name: string;
    created_at: string;

    status: "processing" | "completed" | "failed";

    successful_resumes: number;
    failed_resumes: number;

    user_email: string;
}

// Define the props for the HistoryPanel components
interface Props {
    showHistory: boolean;
    setShowHistory: React.Dispatch<React.SetStateAction<boolean>>;
    currentSessionId?: string;
}

const statusConfig = {
    processing: {
        label: "Processing",
        className: "bg-yellow-100 text-yellow-700",
    },
    completed: {
        label: "Completed",
        className: "bg-green-100 text-green-700",
    },
    failed: {
        label: "Failed",
        className: "bg-red-100 text-red-700",
    },
};


export default function HistoryPanel({
    showHistory,
    setShowHistory,
    currentSessionId
}: Props) {

    const router = useRouter();

    const [isLoading, setIsLoading] = useState(false);

    const [sessions, setSessions] = useState<Session[]>([]);

    const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);

    const activeSessionRef = useRef<HTMLDivElement | null>(null);

    // Load sessions from the backend when the component mounts or when showHistory changes
    useEffect(() => {
        if (!showHistory) return;

        const loadSessions = async () => {
            try {
                setIsLoading(true);

                const res = await api.get("/api/sessions");

                setSessions(res.data);
            } catch (err) {
                console.log(err);
            } finally {
                setIsLoading(false);
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

            await api.delete(
                `/api/sessions/delete/${sessionID}`
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
        finally {
            setDeletingSessionId(null);
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

                {isLoading ? (

                <div className="h-full flex flex-col items-center justify-center">

                    <LoaderCircle
                        size={34}
                        className="animate-spin text-indigo-600"
                    />

                    <p className="mt-4 text-sm text-gray-500">
                        Loading screening history...
                    </p>

                </div>

                ):

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

                    {sessions.map((session) => (

                        <SessionCard
                            key={session.session_id}
                            session={session}
                            currentSessionId={currentSessionId} 
                            deletingSessionId={deletingSessionId}
                            activeSessionRef={activeSessionRef}
                            loadSession={loadSession}
                            handleDeleteSession={handleDeleteSession}
                            />

                    ))}

                </div>

                )
                }

            </div>

        </div >
    );
}