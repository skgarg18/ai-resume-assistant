import { FileText, Plus, History } from "lucide-react"
import { useRouter } from "next/navigation";



interface NavbarProps {
  variant: "home" | "session";
  setShowHistory: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function Navbar({ variant, setShowHistory }: NavbarProps) {
  const router = useRouter();

  const resetDashboard = () => {

    sessionStorage.clear();
    router.push("/")
  }

  return (

    <nav className="h-16 bg-white border-b px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-2 text-blue-600 font-bold text-xl">
        <FileText className="fill-blue-600 text-white" size={24} />
        ResumeAI
      </div>

      <div className="flex gap-6">

        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowHistory?.(true)}
            className="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50 cursor-pointer"
          >
            <History size={16} /> History
          </button>

        </div>

        {variant === "session" &&

          <div className="flex items-center gap-4">
            <button
              onClick={resetDashboard}
              className="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50 cursor-pointer"
            >
              <Plus size={16} /> New Chat
            </button>
          </div>
        }

      </div>
    </nav>

  )

}