"use client";

import React from "react";
import { CheckCircle2, X } from "lucide-react";

interface FileUploadProps {
  files: File[];
  setFiles: React.Dispatch<React.SetStateAction<File[]>>;
  accept?: string;
}

export default function FileUpload({
  files,
  setFiles,
  accept = ".pdf,.docx",
}: FileUploadProps) {
  // --- ADD FILES ---
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Stop event bubbling to avoid triggering form actions
    e.stopPropagation();

    const selectedFiles = e.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;

    const newFilesArray = Array.from(selectedFiles);

    setFiles((prevFiles) => {
      const fileMap = new Map(
        prevFiles.map((file) => [`${file.name}-${file.size}`, file])
      );

      newFilesArray.forEach((file) => {
        fileMap.set(`${file.name}-${file.size}`, file);
      });

      return Array.from(fileMap.values());
    });

    // Clear target value so the same file can be selected again
    e.target.value = "";
  };

  // --- REMOVE FILE ---
  const removeFile = (fileToRemove: File) => {
    setFiles((prevFiles) =>
      prevFiles.filter(
        (file) =>
          `${file.name}-${file.size}` !==
          `${fileToRemove.name}-${fileToRemove.size}`
      )
    );
  };

  return (
    <div>
      <label className="block text-sm font-semibold mb-2">
        Upload Resumes (PDF, DOCX)
      </label>

      <input
        type="file"
        id="resume-upload"
        multiple
        accept={accept}
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Browse Button + Counter */}
      <div className="flex items-center gap-4">
        <label
          htmlFor="resume-upload"
          className="cursor-pointer px-5 py-2.5 bg-gray-100 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition select-none"
        >
          Browse Files
        </label>
        <span className="text-sm text-gray-500">
          {files.length > 0 ? `${files.length} file(s) selected` : "No files selected"}
        </span>
      </div>

      {/* Uploaded Files Tag List */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4 overflow-auto max-h-40">
          {files.map((file) => (
            <div
              key={`${file.name}-${file.size}`}
              className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-full pl-3 pr-2 py-1 text-sm text-blue-800"
            >
              <CheckCircle2 size={14} className="text-green-600 flex-shrink-0" />
              <span className="truncate max-w-[200px]">{file.name}</span>
              <button
                type="button"
                onClick={() => removeFile(file)}
                className="p-0.5 hover:bg-blue-200 rounded-full transition text-gray-500 hover:text-red-600 cursor-pointer"
                title="Remove file"
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}