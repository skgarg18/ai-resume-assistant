

interface TopResumeListInterface{
    results: any[];
    selectedCandidate: any;
    setSelectedCandidate: React.Dispatch<React.SetStateAction<any | null>>;
}

export default function Top_resume_list({results ,selectedCandidate , setSelectedCandidate}:TopResumeListInterface){

  
    return (
        <aside className="h-full bg-white border-r flex flex-col shrink-0">
              <div className="p-4 border-b">
                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Candidates</h2>
                {/* <div className="relative">
                  <Search className="absolute left-3 top-2.5 text-gray-400" size={16} />
                  <input
                    type="text"
                    placeholder="Search candidates..."
                    className="w-full pl-9 pr-3 py-2 bg-gray-50 border rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div> */}
              </div>
              <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-gray-50">
                {results?.map((candidate) => (
                  <div
                    key={candidate.resume_id}
                    onClick={() => setSelectedCandidate(candidate)}
                    className={`p-4 border rounded-xl cursor-pointer transition-all ${selectedCandidate?.resume_id === candidate.resume_id ? 'border-blue-500 bg-white shadow-sm ring-1 ring-blue-500' : 'bg-white border-gray-200 hover:border-blue-300'}`}
                  >
                    <div className="flex gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold shrink-0">
                        {candidate.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start mb-1">
                          <h3 className="font-bold text-sm truncate text-gray-900">{candidate.name}</h3>
                        </div>

                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="bg-green-500 h-full rounded-full"
                              style={{ width: `${candidate.overall_score || 0}%` }}
                            />
                          </div>
                          <span className="text-xs font-bold text-green-600">
                            {candidate.overall_score || 0}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </aside>
    )
}