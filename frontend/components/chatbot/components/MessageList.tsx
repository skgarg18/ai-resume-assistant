"use client";

import {
    useRef,
    useEffect
} from "react";

import { Dispatch, SetStateAction } from "react";

import { Sparkles, User } from "lucide-react";

import EmailCard from "./EmailCard";

import { Message } from "../types/chat";

import ReactMarkdown from "react-markdown";

interface MessageListProps {
    messages: Message[];

    loading: boolean;

    sessionID: string;

    setLoading: Dispatch<SetStateAction<boolean>>;

    setMessages: Dispatch<SetStateAction<Message[]>>;

}

export default function MessageList({
    messages,
    loading,
    setLoading,
    setMessages,
    sessionID
}: MessageListProps) {

    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {

        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });

    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-5 bg-gray-50/50">

            {messages.map((message, index) => (

                <div
                    key={index}
                    className={`flex ${message.role === "user"
                            ? "justify-end"
                            : "justify-start"
                        }`}
                >

                    <div
                        className={`max-w-[88%] rounded-xl px-4 py-3 shadow-sm ${message.role === "user"
                                ? "bg-blue-600 text-white rounded-tr-none"
                                : "bg-white border text-gray-800 rounded-tl-none"
                            }`}
                    >

                        <div className="flex items-start gap-3">

                            {message.role === "assistant" ? (
                                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                                    <Sparkles
                                        size={14}
                                        className="text-blue-600"
                                    />
                                </div>
                            ) : (
                                <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center shrink-0 mt-0.5">
                                    <User
                                        size={14}
                                        className="text-white"
                                    />
                                </div>
                            )}

                            {message.role === "assistant" &&
                                message.type === "email" ? (

                                <EmailCard
                                    draft_id={message.draft_id}
                                    email_id={message.email_id}
                                    subject={message.subject}
                                    body={message.body}
                                    setLoading={setLoading}
                                    setMessages={setMessages}
                                    sessionID={sessionID}
                                    meeting_metadata={message.meeting_metadata}
                                />

                            ) : (

                                <div className="whitespace-pre-wrap text-xs leading-relaxed mt-0.5 overflow-hidden">
                                    <ReactMarkdown>
                                        {message.content}
                                    </ReactMarkdown>    
                                </div>

                            )}

                        </div>

                    </div>

                </div>

            ))}

            {loading && (
                <div className="flex justify-start">

                    <div className="bg-white border shadow-sm px-4 py-3 rounded-xl rounded-tl-none flex items-center gap-3">

                        <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                            <Sparkles
                                size={14}
                                className="text-blue-600"
                            />
                        </div>

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