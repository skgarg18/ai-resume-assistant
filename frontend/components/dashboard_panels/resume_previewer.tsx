import { useEffect, useRef, useState } from "react";
import { renderAsync } from "docx-preview";

interface ResumePreviewProps {
    url: string;
    fileName: string;
    height?: string;
}

export default function ResumePreview({
    url,
    fileName,
    height = "600px",
}: ResumePreviewProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const extension = fileName.split(".").pop()?.toLowerCase();

    useEffect(() => {
        if (extension !== "docx") return;

        let mounted = true;

        const loadDocx = async () => {
            try {
                setLoading(true);
                setError("");

                if (!containerRef.current) return;

                containerRef.current.innerHTML = "";

                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error("Failed to fetch document.");
                }

                const blob = await response.blob();

                if (!mounted || !containerRef.current) return;

                await renderAsync(blob, containerRef.current, undefined, {
                    className: "docx-preview",
                    inWrapper: true,
                    breakPages: true,
                    ignoreWidth: false,
                    ignoreHeight: false,
                    ignoreFonts: false,
                    renderHeaders: true,
                    renderFooters: true,
                    renderFootnotes: true,
                    renderEndnotes: true,
                });
            } catch (err) {
                console.error(err);
                setError("Unable to preview this document.");
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        loadDocx();

        return () => {
            mounted = false;

            if (containerRef.current) {
                containerRef.current.innerHTML = "";
            }
        };
    }, [url, extension]);

    // ---------------- PDF ----------------

    if (extension === "pdf") {
        return (
            <iframe
                src={url}
                width="80%"
                height={height}
                style={{
                    border: "none",
                    borderRadius: "8px",
                }}
                title={fileName}
            />
        );
    }

    // ---------------- DOCX ----------------

    if (extension === "docx") {
        return (
            <div
                style={{
                    width: "100%",
                    height,
                    overflow: "auto",
                    background: "#ffffff",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                    padding: "20px",
                    boxSizing: "border-box",
                }}
            >
                {loading && (
                    <div
                        style={{
                            textAlign: "center",
                            padding: "20px",
                        }}
                    >
                        Loading document...
                    </div>
                )}

                {error && (
                    <div
                        style={{
                            color: "red",
                            textAlign: "center",
                            padding: "20px",
                        }}
                    >
                        {error}
                    </div>
                )}

                <div ref={containerRef} />
            </div>
        );
    }

    // ---------------- DOC ----------------

    if (extension === "doc") {
        return (
            <div
                style={{
                    height,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexDirection: "column",
                    gap: "12px",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                }}
            >
                <p>
                    Preview for <strong>.doc</strong> files is not supported.
                </p>

                <a
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Open / Download Document
                </a>
            </div>
        );
    }

    // ---------------- Unsupported ----------------

    return (
        <div
            style={{
                height,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
            }}
        >
            Preview not available for this file type.
        </div>
    );
}