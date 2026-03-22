import { useState } from "react";
import {
  Search, Plus, ChevronRight, ChevronDown,
  Check, Circle, Sparkles, Target, X, Flame, Clock, ListTodo, ArrowRight, Loader, Trash2,
} from "lucide-react";
import { useAppContext } from "../context/AppContext";
import { getProgress } from "../utils/taskUtils";
import { postPlan } from "../api/client";
import { getStoredGuestUser } from "../utils/guestUser";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  hasGuestUser: boolean;
  onResetGuestUser: () => void;
}

export default function Sidebar({ collapsed, onToggle, hasGuestUser, onResetGuestUser }: SidebarProps) {
  const { projects, activeProject, setActiveProject, activeFilter, setActiveFilter, addProject, deletedTasks } = useAppContext();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ p1: true });
  const [search, setSearch] = useState("");
  const [showNewTask, setShowNewTask] = useState(false);
  const [newGoal, setNewGoal] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const filters = [
    { id: "urgent", label: "Urgent", icon: <Flame className="w-4 h-4" />, color: "text-red-500" },
    { id: "recent", label: "Recent", icon: <Clock className="w-4 h-4" />, color: "text-amber-500" },
    { id: "all", label: "All Tasks", icon: <ListTodo className="w-4 h-4" />, color: "text-gray-500" },
    { id: "trash", label: "Recently Deleted", icon: <Trash2 className="w-4 h-4" />, color: "text-gray-400", count: deletedTasks.length },
  ];

  const filteredProjects = search.trim()
    ? projects.filter(p =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.tasks.some(t => t.title.toLowerCase().includes(search.toLowerCase()))
      )
    : projects;

  const handleCreateTask = async () => {
    if (!newGoal.trim()) return;
    setCreating(true);
    setCreateError(null);
    try {
      const guestUser = getStoredGuestUser();
      const plan = await postPlan({
        goal: newGoal.trim(),
        horizon: "today",
        available_minutes: 60,
        energy: "medium",
        user_id: guestUser?.user_id,
        phone: guestUser?.phone,
      });
      const totalMin = plan.tiny_first_step.estimated_minutes +
        plan.steps.reduce((acc, s) => acc + s.estimated_minutes, 0);
      addProject({
        id: `plan-${plan.plan_id}`,
        name: newGoal.trim(),
        emoji: "🎯",
        color: "#6366F1",
        tasks: [{
          id: plan.plan_id,
          title: newGoal.trim(),
          done: false,
          urgent: false,
          timeEstimate: `~${totalMin} min`,
          subtasks: [
            { id: "tiny-start", title: plan.tiny_first_step.title, description: plan.tiny_first_step.description, done: false, tinyStart: true },
            ...plan.steps.map(s => ({ id: s.id, title: s.title, description: s.description, done: false, tinyStart: false })),
          ],
        }],
      });
      setNewGoal("");
      setShowNewTask(false);
    } catch (err) {
      setCreateError("Couldn't create plan. Try again.");
    } finally {
      setCreating(false);
    }
  };

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

            {/* Search bar */}
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search..."
                className="w-full pl-8 pr-3 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:border-gray-400 transition-colors bg-white"
              />
              {search && (
                <button onClick={() => setSearch("")} className="absolute right-2 top-1/2 -translate-y-1/2">
                  <X className="w-3.5 h-3.5 text-gray-400 hover:text-gray-600" />
                </button>
              )}
            </div>

            {/* New Task button / inline form */}
            {showNewTask ? (
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 space-y-2">
                <input
                  autoFocus
                  value={newGoal}
                  onChange={e => setNewGoal(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter") handleCreateTask(); if (e.key === "Escape") setShowNewTask(false); }}
                  placeholder="What do you need to do?"
                  className="w-full text-sm bg-white border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-gray-400 text-gray-800 placeholder-gray-400"
                />
                {createError && <p className="text-[11px] text-red-500">{createError}</p>}
                <div className="flex gap-2">
                  <button
                    onClick={handleCreateTask}
                    disabled={!newGoal.trim() || creating}
                    className="flex-1 flex items-center justify-center gap-1.5 py-1.5 bg-gray-900 text-white text-xs font-medium rounded-lg hover:bg-gray-800 disabled:opacity-40 transition-colors"
                  >
                    {creating ? <Loader className="w-3 h-3 animate-spin" /> : <ArrowRight className="w-3 h-3" />}
                    {creating ? "Building..." : "Create with AI"}
                  </button>
                  <button
                    onClick={() => { setShowNewTask(false); setNewGoal(""); setCreateError(null); }}
                    className="px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowNewTask(true)}
                className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-800 transition-colors"
              >
                <Plus className="w-4 h-4" /> New Task
              </button>
            )}
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
                  <span className="flex-1 text-left">{f.label}</span>
                  {"count" in f && (f.count ?? 0) > 0 && (
                    <span className="text-[11px] font-medium text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-md">{f.count}</span>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="px-4 pt-4 pb-2 flex-1 overflow-y-auto">
            <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider px-1 mb-2">Projects</p>
            {filteredProjects.length === 0 && search && (
              <p className="text-[13px] text-gray-400 px-1 py-2">No results for "{search}"</p>
            )}
            <div className="space-y-0.5">
              {filteredProjects.map(p => {
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
            {hasGuestUser && (
              <button
                onClick={onResetGuestUser}
                className="mt-3 text-[11px] text-gray-500 hover:text-gray-900 transition-colors"
              >
                Reset Demo User
              </button>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
