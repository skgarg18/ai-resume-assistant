"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Send, Bot, User } from "lucide-react";

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
      content: "Hello! Ask me anything about the shortlisted candidates.",
    },
  ]);
  const [suggestedQuestion, setSuggestedQuestion] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!names || names.length === 0) return;

    const getRandomName = () => names[Math.floor(Math.random() * names.length)];

    const suggestedQuestions = [
      `What projects did ${getRandomName()} build?`,
      `Does ${getRandomName()} know Python?`,
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
    <div className="w-full h-[600px] bg-white rounded-xl shadow-lg border flex flex-col">
      {/* Header */}
      <div className="border-b p-4 bg-gray-50 rounded-t-xl">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Bot className="text-blue-600" /> Recruiter AI
        </h2>
        <p className="text-sm text-gray-500 mt-1">Chat with shortlisted candidates</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-xl px-4 py-3 ${
                message.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-gray-100 text-black rounded-bl-none"
              }`}
            >
              <div className="flex items-start gap-2">
                {message.role === "assistant" ? (
                  <Bot size={18} className="mt-1 shrink-0 opacity-70" />
                ) : (
                  <User size={18} className="mt-1 shrink-0 opacity-70" />
                )}
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </p>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-4 rounded-xl rounded-bl-none">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-150" />
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-300" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4 bg-gray-50 rounded-b-xl">
        {/* Suggested Questions */}
        {suggestedQuestion.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestedQuestion.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className="text-xs border border-gray-200 bg-white px-3 py-1.5 rounded-full hover:bg-gray-100 hover:border-gray-300 transition text-gray-700 text-left"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about candidates..."
            className="flex-1 border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !question.trim()}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}