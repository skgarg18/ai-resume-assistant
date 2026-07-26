"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { getToken } from "@/lib/auth";

export default function Home() {
    const router = useRouter();

    useEffect(() => {
        const token = getToken();

        if (token) {
            router.replace("/upload");
        } else {
            router.replace("/login");
        }
    }, [router]);

    return (
        <div className="flex h-screen items-center justify-center bg-white">
            <div className="flex flex-col items-center gap-4">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-indigo-600" />

                <p className="text-sm font-medium text-gray-500">
                    Loading...
                </p>
            </div>
        </div>
    );
}