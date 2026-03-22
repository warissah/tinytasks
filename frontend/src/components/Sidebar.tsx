import { useState } from "react";
import {
  Search, Plus, ChevronRight, ChevronDown,
  Check, Circle, Sparkles, Target, X, Flame, Clock, ListTodo,
} from "lucide-react";
import { useAppContext } from "../context/AppContext";
import { getProgress } from "../utils/taskUtils";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { projects, activeProject, setActiveProject, activeFilter, setActiveFilter } = useAppContext();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ p1: true });

  const filters = [
    { id: "urgent", label: "Urgent", icon: <Flame className="w-4 h-4" />, color: "text-red-500" },
    { id: "recent", label: "Recent", icon: <Clock className="w-4 h-4" />, color: "text-amber-500" },
    { id: "all", label: "All Tasks", icon: <ListTodo className="w-4 h-4" />, color: "text-gray-500" },
  ];

  return (
    <>
      {!collapsed && (
        <div className="fixed inset-0 bg-black/20 z-30 lg:hidden" onClick={onToggle} />
      )}

      <aside className={`
        fixed lg:sticky top-0 left-0 h-screen z-40 flex flex-col
        bg-white border-r border-gray-200/80
        transition-all duration-300 ease-in-out
        ${collapsed ? "-translate-x-full lg:translate-x-0 lg:w-0 lg:border-0 lg:overflow-hidden" : "translate-x-0 w-72"}
      `}
        style={{ fontFamily: "'DM Sans', sans-serif" }}
      >
        <div className="w-72 flex flex-col h-full">
          <div className="px-4 pt-5 pb-3">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center">
                  <Target className="w-4 h-4 text-white" />
                </div>
                <span className="font-semibold text-gray-900 text-[15px]">TinyTasks</span>
              </div>
              <button onClick={onToggle} className="lg:hidden p-1 rounded-md hover:bg-gray-100">
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>

            <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg border border-gray-200 text-gray-400 text-sm hover:border-gray-300 hover:bg-gray-50 transition-all mb-3">
              <Search className="w-3.5 h-3.5" />
              <span className="flex-1 text-left">Search...</span>
              <kbd className="text-[10px] font-mono bg-gray-100 px-1.5 py-0.5 rounded text-gray-400">⌘K</kbd>
            </button>

            <button className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-800 transition-colors">
              <Plus className="w-4 h-4" /> New Task
            </button>
          </div>

          <div className="px-4 pt-2 pb-1">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider px-1 mb-2">Filters</p>
            <div className="space-y-0.5">
              {filters.map(f => (
                <button
                  key={f.id}
                  onClick={() => { setActiveFilter(f.id); setActiveProject(null); }}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all ${
                    activeFilter === f.id && !activeProject ? "bg-gray-100 text-gray-900 font-medium" : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <span className={f.color}>{f.icon}</span>
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="px-4 pt-4 pb-2 flex-1 overflow-y-auto">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider px-1 mb-2">Projects</p>
            <div className="space-y-0.5">
              {projects.map(p => {
                const progress = getProgress(p.tasks);
                const isActive = activeProject === p.id;
                const isExpanded = expanded[p.id];
                return (
                  <div key={p.id}>
                    <button
                      onClick={() => { setActiveProject(p.id); setActiveFilter(null); }}
                      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all group ${
                        isActive ? "bg-gray-100 text-gray-900 font-medium" : "text-gray-600 hover:bg-gray-50"
                      }`}
                    >
                      <button
                        onClick={e => { e.stopPropagation(); setExpanded(x => ({ ...x, [p.id]: !x[p.id] })); }}
                        className="p-0.5 -ml-0.5 rounded hover:bg-gray-200 transition-colors"
                      >
                        {isExpanded
                          ? <ChevronDown className="w-3 h-3 text-gray-400" />
                          : <ChevronRight className="w-3 h-3 text-gray-400" />
                        }
                      </button>
                      <span>{p.emoji}</span>
                      <span className="flex-1 text-left truncate">{p.name}</span>
                      <span className="text-[11px] text-gray-400 font-mono">{progress}%</span>
                    </button>

                    {isExpanded && (
                      <div className="ml-6 pl-3 border-l border-gray-100 mt-0.5 mb-1 space-y-0.5">
                        {p.tasks.map(t => (
                          <div key={t.id} className="flex items-center gap-2 px-2 py-1.5 rounded-md text-[13px] text-gray-500 hover:bg-gray-50 transition-colors cursor-default">
                            {t.done
                              ? <Check className="w-3 h-3 text-emerald-500 flex-shrink-0" />
                              : <Circle className="w-3 h-3 text-gray-300 flex-shrink-0" />
                            }
                            <span className={`truncate ${t.done ? "line-through text-gray-400" : ""}`}>{t.title}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="px-5 py-4 border-t border-gray-100">
            <div className="flex items-center gap-2 text-[11px] text-gray-400">
              <Sparkles className="w-3 h-3" />
              <span>Tiny steps, big progress</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
