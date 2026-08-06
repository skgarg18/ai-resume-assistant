"use client";

import { useRef, useEffect, Dispatch, SetStateAction } from "react";
import { Sparkles, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import EmailCard from "./EmailCard";
import CandidateSearchMessage from "./chat_type_res/candidate_search_type";
import CandidateLookupMessage from "./chat_type_res/candidate_lookup_type";
import CandidateComparisonMessage from "./chat_type_res/candidate_comparision_type";

import { Message } from "../types/chat";

interface MessageListProps {
    messages: Message[];
    loading: boolean;
    sessionID: string;
    setLoading: Dispatch<SetStateAction<boolean>>;
    setMessages: Dispatch<SetStateAction<Message[]>>;
    setSelectedCandidate: React.Dispatch<React.SetStateAction<any | null>>;
    results: any[];
}

export default function MessageList({
    messages,
    loading,
    setLoading,
    setMessages,
    sessionID,
    setSelectedCandidate,
    results
}: MessageListProps) {

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages]);

    const renderSparklesAvatar = () => (
        <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
            <Sparkles size={14} className="text-blue-600" />
        </div>
    );

    const renderMessageContent = (message: Message) => {
        // User Message (Horizontal layout)
        if (message.role === "user") {
            return (
                <div className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                        <User size={14} className="text-blue-600" />
                    </div>
                    <div className="whitespace-pre-wrap text-xs leading-relaxed mt-0.5 overflow-x-auto">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                        </ReactMarkdown>
                    </div>
                </div>
            );
        }

        // Email Assistant Workflow (Vertical layout)
        if (message.type === "email") {
            return (
                <div className="flex flex-col items-start gap-3">
                    {renderSparklesAvatar()}
                    <EmailCard
                        draft_id={message.draft_id}
                        email_candidates={message.email_candidates}
                        subject={message.subject}
                        body={message.body}
                        setLoading={setLoading}
                        setMessages={setMessages}
                        sessionID={sessionID}
                        meeting_metadata={message.meeting_metadata}
                        selected_email_candidate={message.selected_email_candidate}
                        cc_emails={message.cc_emails}
                        bcc_emails={message.bcc_emails}
                        setSelectedCandidate={setSelectedCandidate}
                        results={results}
                    />
                </div>
            );
        }

        // Specialized Chat Workflows (Vertical layouts)
        if (message.type === "chat" && message.details) {
            switch (message.details.type) {
                case "candidate_search":
                    return (
                        <div className="flex flex-col items-start gap-3">
                            {renderSparklesAvatar()}
                            <CandidateSearchMessage
                                candidates={message.details.candidates}
                                setSelectedCandidate={setSelectedCandidate}
                                results={results}
                            />
                        </div>
                    );

                case "candidate_lookup":
                    return (
                        <div className="flex flex-col items-start gap-3">
                            {renderSparklesAvatar()}
                            <CandidateLookupMessage
                                candidates={message.details.candidates}
                                missingNames={message.details.missing_names}
                                setSelectedCandidate={setSelectedCandidate}
                                results={results}
                            />
                        </div>
                    );

                case "candidate_comparison":
                    return (
                        <div className="flex flex-col items-start gap-3">
                            {renderSparklesAvatar()}
                            <CandidateComparisonMessage
                                data={message.details.data}
                            />
                        </div>
                    );
            }
        }

        // Standard Assistant Chat Response (Horizontal layout)
        return (
            <div className="flex items-start gap-3">
                {renderSparklesAvatar()}
                <div className="whitespace-pre-wrap text-xs leading-relaxed mt-0.5 overflow-x-auto">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                    </ReactMarkdown>
                </div>
            </div>
        );
    };

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-5 bg-gray-50/50">
            {messages.map((message, index) => (
                <div
                    key={index}
                    className={`flex ${
                        message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                >
                    <div
                        className={`max-w-[88%] rounded-xl px-4 py-3 shadow-sm ${
                            message.role === "user"
                                ? "bg-blue-600 text-white rounded-tr-none"
                                : "bg-white border text-gray-800 rounded-tl-none"
                        }`}
                    >
                        {renderMessageContent(message)}
                    </div>
                </div>
            ))}

            {loading && (
                <div className="flex justify-start">
                    <div className="bg-white border shadow-sm px-4 py-3 rounded-xl rounded-tl-none flex items-center gap-3">
                        {renderSparklesAvatar()}
                        <div className="flex gap-1.5 mt-1">
                            <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" />
                            <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce delay-150" />
                            <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce delay-300" />
                        </div>
                    </div>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}