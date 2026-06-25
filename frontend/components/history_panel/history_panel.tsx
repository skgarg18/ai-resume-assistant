"use client";

import axios from "axios";
import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

interface Session {
    session_id: string;
    session_name: string;
    created_at: string;
}

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

    const loadSession = (sessionId: string) => {
        sessionStorage.setItem(
            "session_id",
            sessionId
        );

        setShowHistory(false);

        router.push(`/${sessionId}`)
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

                                return (

                                    <button
                                        key={session.session_id}
                                        disabled={isCurrent}
                                        onClick={() =>
                                            loadSession(session.session_id)
                                        }
                                        className={`
                                            mx-2

                                            rounded-xl
                                            border

                                            p-2

                                            text-left

                                            transition-all duration-200

                                            ${isCurrent
                                                        ? `
                                                        bg-indigo-50
                                                        border-indigo-300
                                                        shadow-sm
                                                        cursor-default
                                                      `
                                                        : `
                                                        border-gray-200
                                                        hover:bg-slate-50
                                                        hover:border-slate-300
                                                        cursor-pointer
                                                      `
                                                    }
                                        `}
                                    >

                                        <div className="flex items-start justify-between gap-2">

                                            <div className="flex-1">

                                                <div
                                                    className={`
                                                        font-medium
                                                        text-sm
                                                        leading-5

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

                                                px-2.5 py-1
                                                rounded-full

                                                shrink-0
                                            "
                                                >
                                                    Active
                                                </span>

                                            )}

                                        </div>

                                    </button>

                                );
                            })}

                        </div>

                    )
                }

            </div>

        </div >
    );
}