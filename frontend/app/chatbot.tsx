"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Send, Sparkles, User } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatBotProps {
  names: string[];
}

export default function ChatBot({ names }: ChatBotProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! Ask me anything about the shortlisted candidates. I can compare them or dive deep into their specific experience.",
    },
  ]);
  const [suggestedQuestion, setSuggestedQuestion] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
      const response = await axios.post("http://127.0.0.1:8555/api/chat", {
        question: currentQuestion,
        chat_history: messages.slice(-6),
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.data.answer,
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Failed to fetch response from server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      sendMessage();
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
              <div className="flex items-start gap-3">
                {message.role === "assistant" ? (
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles size={14} className="text-blue-600" />
                  </div>
                ) : (
                  <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center shrink-0 mt-0.5">
                    <User size={14} className="text-white" />
                  </div>
                )}
                <p className="whitespace-pre-wrap text-sm leading-relaxed mt-0.5">
                  {message.content}
                </p>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm px-4 py-3 rounded-xl rounded-tl-none flex items-center gap-3">
               <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                  <Sparkles size={14} className="text-blue-600" />
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

      {/* Input Area */}
      <div className="p-4 border-t bg-white shrink-0">
        {/* Suggested Questions */}
        {suggestedQuestion.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestedQuestion.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className="text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 px-3 py-1.5 rounded-full transition text-left font-medium"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-2 items-center bg-gray-50 border rounded-xl px-2 py-2 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about the resumes..."
            className="flex-1 bg-transparent px-2 py-1 text-sm outline-none"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !question.trim()}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}