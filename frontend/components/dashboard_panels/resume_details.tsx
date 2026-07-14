"use client";

import { useState } from "react";
import {Phone , Mail , FileText , X} from "lucide-react"

interface ResumeDetailsInterface{
    selectedCandidate: any;
}

export default function ResumeDetails({selectedCandidate} : ResumeDetailsInterface){

    const [showResume, setShowResume] = useState(false);

    console.log(selectedCandidate)

    return(
                <div className="bg-white rounded-xl border shadow-sm flex flex-col h-full overflow-hidden">
                  {/* Header */}
                  <div className="p-4 border-b flex justify-between items-center bg-white shrink-0 z-1">
                    {/* Name */}
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedCandidate.name}</h2>
                    </div>

                    {/* Contact details and resume pdf previewer */}
                    <div className="flex gap-3">
                      <div className="relative group">
                        <button className="p-3 rounded-xl border hover:bg-gray-50 transition cursor-pointer">
                          <Phone size={20} />
                        </button>

                        <div
                          className="
                              absolute
                              top-full
                              left-1/2
                              -translate-x-1/2
                              mt-2
                              px-3
                              py-2
                              rounded-lg
                              bg-gray-900
                              text-white
                              text-xs
                              whitespace-nowrap
                              opacity-0
                              invisible
                              group-hover:opacity-100
                              group-hover:visible
                              transition-all
                              z-50
                            "
                        >
                          {selectedCandidate.contact}
                        </div>
                      </div>

                      <div className="relative group">
                        <button

                          className="p-3 rounded-xl border hover:bg-gray-50 transition cursor-pointer">
                          <Mail size={20} />
                        </button>

                        <div
                          className="
                              absolute
                              top-full
                              left-1/2
                              -translate-x-1/2
                              mt-2
                              px-3
                              py-2
                              rounded-lg
                              bg-gray-900
                              text-white
                              text-xs
                              whitespace-nowrap
                              opacity-0
                              invisible
                              group-hover:opacity-100
                              group-hover:visible
                              transition-all
                              z-50
                            "
                        >
                          {selectedCandidate.email}
                        </div>
                      </div>

                      <div className="relative group">
                        <button
                          onClick={() => setShowResume(true)}
                          className="p-3 rounded-xl border hover:bg-gray-50 transition cursor-pointer">
                          <FileText size={20} />
                        </button>
                      </div>
                    </div>

                    {/* Match Score */}
                    <div className="bg-green-50 px-4 py-2 rounded-lg border border-green-100 flex flex-col items-center">
                      <span className="text-xs text-green-700 font-bold uppercase">Match Score</span>
                      <span className="text-xl font-black text-green-600 leading-none">
                        {selectedCandidate.score || 0}%
                      </span>
                    </div>
                  </div>

                  {/* Top Cards */}
                  {/* MAIN CONTENT */}
                  <div className="flex flex-col gap-4 p-4 overflow-y-auto">

                    {/* SUMMARY */}
                    <div className="border rounded-xl p-5">
                      <h3 className="font-bold uppercase text-sm text-gray-800 mb-4">
                        Summary
                      </h3>

                      <ul className="list-disc list-outside pl-5 space-y-2.5 text-justify">
                          {selectedCandidate.summary?.map(
                            (point: string, index: number) => (
                              <li
                                key={index}
                                className="text-xs font-semibold text-gray-700 leading-relaxed pl-1"
                              >
                                {point}
                              </li>
                            )
                          )}
                      </ul>
                    </div>

                    {/* SKILLS SECTION */}
                    <div className="grid grid-cols-2 gap-4">

                      {/* MATCHED */}
                      <div className="border rounded-xl p-5">

                        <h3 className="font-bold uppercase text-sm text-gray-800 mb-4">
                          Top Matched Skills
                        </h3>

                        <div className="flex flex-wrap gap-2">

                          {selectedCandidate.matched_skills?.map(
                            (skill: string) => (
                              <span
                                key={skill}
                                className="
                                    px-2 py-2
                                    rounded-full
                                    bg-green-50
                                    border
                                    border-green-200
                                    text-green-700
                                    text-xs
                                    font-medium
                                  "
                              >
                                {skill}
                              </span>
                            )
                          )}

                        </div>
                      </div>

                      {/* MISSING */}
                      <div className="border rounded-xl p-5">

                        <h3 className="font-bold uppercase text-sm text-gray-800 mb-4">
                          Missing Skills
                          <span className="ml-2 text-xs text-red-500">
                            ({selectedCandidate.missing_skills?.length || 0})
                          </span>
                        </h3>

                        <div className="flex flex-wrap gap-2">

                          {selectedCandidate.missing_skills?.map(
                            (skill: string) => (
                              <span
                                key={skill}
                                className="
                                    px-3 py-2
                                    rounded-full
                                    bg-red-50
                                    border
                                    border-red-200
                                    text-red-700
                                    text-xs
                                    font-medium
                                  "
                              >
                                {skill}
                              </span>
                            )
                          )}

                        </div>

                      </div>

                    </div>

                  </div>

                  {/* PDF MODAL */}
                  {showResume && (
                    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center">

                      {/* Close Button */}
                      <button
                        onClick={() => setShowResume(false)}
                        className="
                              absolute
                              top-5
                              right-5
                              z-60
                              bg-white
                              border
                              rounded-full
                              p-2
                              shadow-md
                              hover:bg-gray-100
                              cursor-pointer
                            "
                      >
                        <X size={20} />
                      </button>

                      {/* Scrollable Container */}
                      <div className="w-full h-full overflow-auto py-8">

                        {/* Paper */}
                        <div
                          className="
                                    bg-white
                                    w-200
                                    min-h-275
                                    mx-auto
                                    rounded-lg
                                    shadow-2xl
                                    overflow-hidden
                                  "
                        >
                          {/* <iframe
                            src={`${selectedCandidate.signed_file_url}#toolbar=0&view=FitH`}
                            className="w-full h-275"
                            title="Resume PDF"
                          /> */}

                          <iframe src={`https://docs.google.com/viewer?url=${selectedCandidate.signed_file_url}&embedded=true`} width="100%" height="600px"></iframe>

                          
                        </div>

                      </div>
                    </div>
                  )}




                </div>
    )
}