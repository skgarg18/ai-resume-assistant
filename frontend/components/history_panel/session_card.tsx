import {
    Trash2,
    LoaderCircle,
    User
} from "lucide-react";


interface Session {
    session_id: string;
    session_name: string;
    created_at: string;

    status: "processing" | "completed" | "failed";

    successful_resumes: number;
    failed_resumes: number;

    user_email: string;
}

interface Props{
    session : Session,
    currentSessionId?:string,
    deletingSessionId?:string | null,
    activeSessionRef: React.RefObject<HTMLDivElement | null>;

    loadSession: (sessionId: string) => void;

    handleDeleteSession: (sessionId: string) => void;
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

export default function SessionCard(
    { session , currentSessionId , deletingSessionId , activeSessionRef , loadSession , handleDeleteSession }: Props
) {



    const isCurrent =
        session.session_id === currentSessionId;

    const isDeleting =
        deletingSessionId === session.session_id;

    const status =
        statusConfig[session.status];

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
                    disabled={isCurrent
                        || session.status !== "completed"
                    }
                    onClick={() =>
                        loadSession(session.session_id)
                    }
                    className={`
                                                   flex-1
                                                   min-w-0

                                                   p-2

                                                   text-left

                                                   ${isCurrent || session.status !== "completed"
                            ? "cursor-default"
                            : "cursor-pointer"
                        }
                                               `}
                >

                    <div className="flex items-start justify-between gap-3">

                        <div className="flex-1 min-w-0">

                            <div
                                className={`
                                                                font-medium
                                                                text-sm
                                                                truncate
                                                                ${isCurrent
                                        ? "text-indigo-900"
                                        : "text-gray-700"}
                                                            `}
                            >
                                {session.session_name}
                            </div>

                            <div className="flex items-center justify-between gap-3 mt-1">

                                <div
                                    className={`
                                                                        text-xs
                                                                        font-medium
                                                                        px-2 py-1
                                                                        rounded-full
                                                                        ${status.className}
                                                                    `}
                                >
                                    {status.label}
                                </div>



                                {session.status !== "processing" &&

                                    <div className="flex items-center gap-2 text-xs">

                                        {session.successful_resumes > 0 &&
                                            <span className="text-green-600 font-medium">
                                                ✓ {session.successful_resumes} Successful
                                            </span>
                                        }

                                        {session.failed_resumes > 0 &&

                                            <span className="text-red-600 font-medium">
                                                ✕ {session.failed_resumes} Failed
                                            </span>
                                        }
                                    </div>
                                }

                                {isCurrent && (

                                    <span
                                        className="
                                                                    bg-indigo-100
                                                                    text-indigo-700
                                                                    text-[11px]
                                                                    font-medium
                                                                    px-2 py-1
                                                                    rounded-full
                                                                "
                                    >
                                        Active
                                    </span>

                                )
                                }
                            </div>

                            <div className="flex gap-3 mt-1 justify-between">


                                <div className="text-xs text-gray-400 mt-1">

                                    {new Date(
                                        session.created_at
                                    ).toLocaleString()}

                                </div>

                                <div className="flex items-center gap-2">
                                    <User
                                        size={14}
                                        className="text-gray-400"
                                    />

                                    <div className="text-xs text-gray-400 mt-1">
                                        {session.user_email}
                                    </div>
                                </div>

                            </div>

                        </div>

                    </div>

                </button>


                {/* DELETE BUTTON */}

                {!isCurrent && session.status !== "processing"
                    && (

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

}