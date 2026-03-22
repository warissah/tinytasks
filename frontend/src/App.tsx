import { useState, useCallback, useEffect, useRef } from "react";
import { Target, Menu } from "lucide-react";
import { AppContext } from "./context/AppContext";
import type { Project, DeletedTask } from "./context/AppContext";
import { INITIAL_PROJECTS } from "./data/initialData";
import Onboarding from "./components/Onboarding";
import Sidebar from "./components/Sidebar";
import MainCanvas from "./components/MainCanvas";
import AIChatInput from "./components/AIChatInput";
import type { PlanResponse } from "./api/client";
import { getDemoEvents } from "./api/client";

export default function App() {
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [projects, setProjects] = useState(INITIAL_PROJECTS);
  const [activeProject, setActiveProject] = useState<string | null>("p1");
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [planResponse, setPlanResponse] = useState<PlanResponse | null>(null);
  const [deletedTasks, setDeletedTasks] = useState<DeletedTask[]>([]);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userPhone, setUserPhone] = useState<string | null>(null);
  const [whatsAppNudge, setWhatsAppNudge] = useState<{ message: string; two_minute_action: string } | null>(null);
  const lastEventTs = useRef<number | undefined>(undefined);

  // Poll for WhatsApp-triggered events every 4 seconds
  useEffect(() => {
    const poll = async () => {
      try {
        const events = await getDemoEvents(lastEventTs.current);
        if (events.length === 0) return;
        lastEventTs.current = Math.max(...events.map(e => e.timestamp));
        for (const ev of events) {
          if (ev.type === "task_complete") {
            // Mark the first incomplete subtask done across all projects
            setProjects(prev => {
              let marked = false;
              return prev.map(p => ({
                ...p,
                tasks: p.tasks.map(t => {
                  if (marked) return t;
                  const firstIncomplete = t.subtasks?.find(s => !s.done);
                  if (!firstIncomplete) return t;
                  marked = true;
                  const updated = t.subtasks.map(s => s.id === firstIncomplete.id ? { ...s, done: true } : s);
                  const allDone = updated.every(s => s.done);
                  return { ...t, subtasks: updated, done: allDone };
                }),
              }));
            });
          } else if (ev.type === "nudge") {
            setWhatsAppNudge({ message: ev.data.message, two_minute_action: ev.data.two_minute_action });
          } else if (ev.type === "new_plan") {
            const plan = ev.data.plan as import("./api/client").PlanResponse;
            const goal = ev.data.goal || plan.summary;
            const project = planToProject(plan, goal);
            setProjects(prev => [project, ...prev]);
            setActiveProject(project.id);
            setActiveFilter(null);
          }
        }
      } catch {
        // silently ignore poll errors
      }
    };
    const id = setInterval(poll, 4000);
    return () => clearInterval(id);
  }, []);

  const planToProject = (plan: PlanResponse, goal: string): Project => {
    const totalMin = plan.tiny_first_step.estimated_minutes +
      plan.steps.reduce((acc, s) => acc + s.estimated_minutes, 0);
    return {
      id: `plan-${plan.plan_id}`,
      name: goal,
      emoji: "🎯",
      color: "#F59E0B",
      tasks: [{
        id: plan.plan_id,
        title: goal,
        done: false,
        urgent: false,
        timeEstimate: `~${totalMin} min`,
        subtasks: [
          { id: "tiny-start", title: plan.tiny_first_step.title, description: plan.tiny_first_step.description, done: false, tinyStart: true },
          ...plan.steps.map(s => ({ id: s.id, title: s.title, description: s.description, done: false, tinyStart: false })),
        ],
      }],
    };
  };

  const handlePlanComplete = (plan: PlanResponse, goal: string, email: string, phone: string) => {
    setUserEmail(email);
    setUserPhone(phone);
    setPlanResponse(plan);
    const planProject = planToProject(plan, goal);
    setProjects(prev => [planProject, ...prev]);
    setActiveProject(planProject.id);
    setActiveFilter(null);
    setShowOnboarding(false);
  };

  const toggleSubtask = useCallback((taskId: string, subtaskId: string) => {
    setProjects(prev =>
      prev.map(p => ({
        ...p,
        tasks: p.tasks.map(t => {
          if (t.id !== taskId) return t;
          const updatedSubtasks = t.subtasks.map(s =>
            s.id === subtaskId ? { ...s, done: !s.done } : s
          );
          const allDone = updatedSubtasks.length > 0 && updatedSubtasks.every(s => s.done);
          return { ...t, subtasks: updatedSubtasks, done: allDone };
        }),
      }))
    );
  }, []);

  const addSubtask = useCallback((projectId: string, taskId: string, title: string) => {
    setProjects(prev =>
      prev.map(p => p.id !== projectId ? p : {
        ...p,
        tasks: p.tasks.map(t => {
          if (t.id !== taskId) return t;
          const newSubtask = { id: `s-${Date.now()}`, title, done: false };
          // Insert before the first done subtask so all todos stay grouped together
          const firstDoneIdx = t.subtasks.findIndex(s => s.done);
          const newSubtasks = firstDoneIdx === -1
            ? [...t.subtasks, newSubtask]
            : [...t.subtasks.slice(0, firstDoneIdx), newSubtask, ...t.subtasks.slice(firstDoneIdx)];
          return { ...t, subtasks: newSubtasks };
        }),
      })
    );
  }, []);

  const removeSubtask = useCallback((projectId: string, taskId: string, subtaskId: string) => {
    setProjects(prev =>
      prev.map(p => p.id !== projectId ? p : {
        ...p,
        tasks: p.tasks.map(t => t.id !== taskId ? t : {
          ...t,
          subtasks: t.subtasks.filter(s => s.id !== subtaskId),
        }),
      })
    );
  }, []);

  const deleteTask = useCallback((projectId: string, taskId: string) => {
    setProjects(prev => {
      const project = prev.find(p => p.id === projectId);
      if (project) {
        const task = project.tasks.find(t => t.id === taskId);
        if (task) {
          setDeletedTasks(d => [
            { task, projectId, projectName: project.name, projectEmoji: project.emoji, projectColor: project.color },
            ...d.slice(0, 9),
          ]);
        }
        // If the project will become empty, navigate away
        if (project.tasks.length === 1) {
          setActiveProject(null);
          setActiveFilter("all");
        }
      }
      return prev
        .map(p => p.id !== projectId ? p : { ...p, tasks: p.tasks.filter(t => t.id !== taskId) })
        .filter(p => p.tasks.length > 0);
    });
  }, []);

  const restoreTask = useCallback((taskId: string) => {
    setDeletedTasks(prev => {
      const entry = prev.find(d => d.task.id === taskId);
      if (!entry) return prev;
      setProjects(projects => {
        const projectExists = projects.some(p => p.id === entry.projectId);
        if (projectExists) {
          return projects.map(p => p.id !== entry.projectId ? p : {
            ...p,
            tasks: [...p.tasks, entry.task],
          });
        }
        // Restore the project too
        const restoredProject: Project = {
          id: entry.projectId,
          name: entry.projectName,
          emoji: entry.projectEmoji,
          color: entry.projectColor,
          tasks: [entry.task],
        };
        return [restoredProject, ...projects];
      });
      return prev.filter(d => d.task.id !== taskId);
    });
  }, []);

  const addProject = useCallback((project: Project) => {
    setProjects(prev => [project, ...prev]);
    setActiveProject(project.id);
    setActiveFilter(null);
  }, []);

  const contextValue = {
    projects, activeProject, setActiveProject,
    activeFilter, setActiveFilter,
    toggleSubtask, addSubtask, removeSubtask, deleteTask, restoreTask, deletedTasks, addProject,
    planResponse, setPlanResponse,
    sessionActive: false, setSessionActive: () => {},
    whatsAppNudge, clearWhatsAppNudge: () => setWhatsAppNudge(null),
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className="min-h-screen" style={{ fontFamily: "'DM Sans', sans-serif", background: "#FAFBFC" }}>
        {showOnboarding && (
          <Onboarding onComplete={handlePlanComplete} />
        )}

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
