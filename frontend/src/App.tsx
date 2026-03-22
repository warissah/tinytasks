import { useState, useCallback } from "react";
import { Target, Menu } from "lucide-react";
import { AppContext } from "./context/AppContext";
import { INITIAL_PROJECTS } from "./data/initialData";
import Onboarding from "./components/Onboarding";
import Sidebar from "./components/Sidebar";
import MainCanvas from "./components/MainCanvas";
import AIChatInput from "./components/AIChatInput";

export default function App() {
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [projects, setProjects] = useState(INITIAL_PROJECTS);
  const [activeProject, setActiveProject] = useState<string | null>("p1");
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const toggleSubtask = useCallback((taskId: string, subtaskId: string) => {
    setProjects(prev =>
      prev.map(p => ({
        ...p,
        tasks: p.tasks.map(t => {
          if (t.id !== taskId) return t;
          return {
            ...t,
            subtasks: t.subtasks.map(s =>
              s.id === subtaskId ? { ...s, done: !s.done } : s
            ),
          };
        }),
      }))
    );
  }, []);

  const contextValue = {
    projects, activeProject, setActiveProject,
    activeFilter, setActiveFilter, toggleSubtask,
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className="min-h-screen" style={{ fontFamily: "'DM Sans', sans-serif", background: "#FAFBFC" }}>
        {showOnboarding && <Onboarding onComplete={() => setShowOnboarding(false)} />}

        <div className="flex">
          <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(c => !c)} />

          <div className="flex-1 min-w-0 relative">
            <div className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-gray-200/60 px-4 py-3 flex items-center gap-3 lg:hidden">
              <button onClick={() => setSidebarCollapsed(false)} className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-gray-900" />
                <span className="font-semibold text-sm text-gray-900">TinyTasks</span>
              </div>
            </div>

            {sidebarCollapsed && (
              <button
                onClick={() => setSidebarCollapsed(false)}
                className="hidden lg:flex fixed top-4 left-4 z-20 items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md text-sm text-gray-600 hover:text-gray-900 transition-all"
              >
                <Menu className="w-4 h-4" />
              </button>
            )}

            <MainCanvas />
            <AIChatInput />
          </div>
        </div>
      </div>
    </AppContext.Provider>
  );
}
