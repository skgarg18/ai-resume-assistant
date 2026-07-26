"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck } from "lucide-react";

import api from "@/lib/axios";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
    const router = useRouter();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();

        setLoading(true);
        setError("");

        try {
            const response = await api.post("/auth/login", {
                email,
                password,
            });

            setToken(response.data.access_token);

            router.replace("/");
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ??
                "Invalid email or password."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 flex items-center justify-center p-6">

            <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl border border-slate-200 p-10">

                {/* Logo */}

                <div className="flex justify-center mb-6">

                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 shadow-lg">

                        <ShieldCheck className="h-8 w-8 text-white" />

                    </div>

                </div>

                {/* Heading */}

                <div className="text-center mb-8">

                    <h1 className="text-3xl font-bold text-slate-900">
                        Resume AI
                    </h1>

                    <p className="mt-2 text-slate-500">
                        Sign in to access your dashboard
                    </p>

                </div>

                <form
                    onSubmit={handleLogin}
                    className="space-y-5"
                >

                    {/* Email */}

                    <div>

                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Email
                        </label>

                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Email ID"
                            required
                            className="w-full text-black rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition-all duration-200 placeholder:text-slate-400 focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                        />

                    </div>

                    {/* Password */}

                    <div>

                        <label className="block text-sm font-medium text-slate-700 mb-2">
                            Password
                        </label>

                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                            className="w-full text-black rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition-all duration-200 placeholder:text-slate-400 focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                        />

                    </div>

                    {error && (

                        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">

                            {error}

                        </div>

                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="mt-2 w-full rounded-xl bg-blue-600 py-3 text-base font-semibold text-white transition-all duration-200 hover:bg-blue-700 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {loading ? "Signing in..." : "Login"}
                    </button>

                </form>

                <div className="mt-8 border-t border-slate-200 pt-5 text-center text-xs text-slate-400">

                    Secure access to Resume AI

                </div>

            </div>

        </div>
    );
}