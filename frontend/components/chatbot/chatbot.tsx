"use client";

import { useState, useRef, useEffect } from "react";
import api from "@/lib/axios";
// import axios from "axios";
import { Sparkles } from "lucide-react";

import MessageList from "./components/MessageList";

import ChatInput from "./components/ChatInput";

import type { Message } from "./types/chat";

interface ChatBotProps {
  names: string[];
  sessionID: string;
}

export default function ChatBot({ names, sessionID }: ChatBotProps) {



  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      type: "chat",
      content: "Hello! Ask me anything about the shortlisted candidates. I can compare them or dive deep into their specific experience.",
    },
  ]);

  const [suggestedQuestion, setSuggestedQuestion] = useState<string[]>([]);


  // Load chat history from the backend when the component mounts or when sessionID changes
  const loadChatHistory = async () => {

    try {
      const res = await api.get(
        `/api/chat-history/${sessionID}`
      );

      const chatRows = res.data;

      // console.log("chat history", chatRows)

      if (chatRows) {

        const DEFAULT_MESSAGE: Message = {
          role: "assistant",
          type: "chat",
          content:
            "Hello! Ask me anything about the shortlisted candidates. I can compare them or dive deep into their specific experience.",
        };

        const formattedMessages: Message[] = [
          DEFAULT_MESSAGE,

          ...chatRows.flatMap((row: any) => {

            const messages: Message[] = [];

            messages.push({
              role: "user",
              content: row.user_message,
            });

            if (row.message_type === "email") {

              messages.push({
                role: "assistant",
                type: "email",

                draft_id: row.draft_id,

                email_ids: row.email_ids,
                subject: row.email_subject,

                selected_email: row.selected_email,
                body: row.email_body,

                meeting_metadata: row.meeting_metadata
              });

            } else {

              messages.push({
                role: "assistant",
                type: "chat",
                content: row.assistant_message,
              });

            }

            return messages;
          }),
        ];

        setMessages(formattedMessages);
      }

    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };


  // Load chat history when the component mounts or when sessionID changes
  useEffect(() => {
    if (sessionID != "") { loadChatHistory() }
  }, [sessionID])


  // Generate suggested questions based on the names of the candidates
  useEffect(() => {
    if (!names || names.length === 0) return;

    const getRandomName = () => names[Math.floor(Math.random() * names.length)];

    const suggestedQuestions = [
      `What projects did ${getRandomName()} build?`,
      names.length >= 2
        ? `Compare ${names[0]} and ${names[1]}`
        : "Who has the strongest technical background?",
      "Who has stronger relevant experience?",
    ];

    setSuggestedQuestion(suggestedQuestions);
  }, [names]);


  // Send a message to the backend and handle the response
  const sendMessage = async () => {
    if (!question.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: question,
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentQuestion = question;
    setQuestion("");

    try {
      setLoading(true);
      const response = await api.post(`/api/${sessionID}/chat`, {
        question: currentQuestion,
        chat_history: messages
          .slice(-6)
          .map((msg) => ({
            role: msg.role,
            content:
              msg.role === "assistant"
                ? (
                  msg.type === "email"
                    ? `Subject: ${msg.subject}\n\n${msg.body}`
                    : msg.content
                )
                : msg.content,
          })),
      });

      if (response.data.type === "chat") {

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            type: "chat",
            content: response.data.message,
          },
        ]);

      } else if (response.data.type === "email") {

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            type: "email",

            draft_id: response.data.draft_id,

            email_ids: response.data.email_ids,
            selected_email: response.data.selected_email,

            subject: response.data.subject,
            body: response.data.body,

            meeting_metadata: response.data.meeting_metadata,

            cc_emails: response.data.cc_emails,

            bcc_emails: response.data.bcc_emails
          },
        ]);

      }
    } catch (error) {
      // console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: "chat",
          content: "Failed to fetch response from server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };


  return (
    // Changed wrapper to fit sidebar dimensions (h-full instead of fixed 600px, removed outer border/shadow)
    <div className="w-full h-full flex flex-col bg-white">
      {/* Header */}
      <div className="border-b p-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 text-gray-800">
          <Sparkles className="text-blue-600" size={20} />
          <h2 className="font-bold text-sm">AI Recruiter Assistant</h2>
        </div>
      </div>

      {/* Messages */}
      <MessageList
        messages={messages}
        loading={loading}
        setLoading={setLoading}
        setMessages={setMessages}
        sessionID={sessionID}
      />

      {/* Input Area */}
      <ChatInput
        question={question}
        setQuestion={setQuestion}
        loading={loading}
        sendMessage={sendMessage}
        suggestedQuestions={suggestedQuestion}
      />
    </div >
  );
}