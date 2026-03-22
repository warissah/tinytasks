import { ChevronRight, Zap, Circle, ShieldAlert, Trash2, RotateCcw } from "lucide-react";
import { useAppContext } from "../context/AppContext";
import { getProgress, getNextTinyStart } from "../utils/taskUtils";
import TaskCard from "./TaskCard";
import type { Task } from "../context/AppContext";

export default function MainCanvas() {
  const { projects, activeProject, activeFilter, toggleSubtask, deleteTask, removeSubtask, restoreTask, deletedTasks, planResponse } = useAppContext();

  let breadcrumb = "All Tasks";
  let displayTasks: Task[] = [];
  let projectColor = "#6366F1";

  if (activeProject) {
    const p = projects.find(x => x.id === activeProject);
    if (p) {
      breadcrumb = p.name;
      displayTasks = p.tasks;
      projectColor = p.color;
    }
  } else if (activeFilter === "urgent") {
    breadcrumb = "Urgent";
    projects.forEach(p => {
      p.tasks.filter(t => t.urgent).forEach(t => displayTasks.push({ ...t, _projectColor: p.color }));
    });
  } else if (activeFilter === "recent") {
    breadcrumb = "Recent";
    projects.forEach(p => {
      displayTasks.push(...p.tasks.slice(0, 2).map(t => ({ ...t, _projectColor: p.color })));
    });
  } else if (activeFilter === "trash") {
    breadcrumb = "Recently Deleted";
  } else {
    breadcrumb = "All Tasks";
    projects.forEach(p => {
      displayTasks.push(...p.tasks.map(t => ({ ...t, _projectColor: p.color })));
    });
  }

  const project = projects.find(x => x.id === activeProject);
  const progress = project ? getProgress(project.tasks) : null;
  const nextTiny = project ? getNextTinyStart(project.tasks) : null;
  const isAIPlan = activeProject === "ai-plan";

  return (
    <div className="flex-1 min-h-screen" style={{ background: "#FAFBFC" }}>
      <div className="max-w-3xl mx-auto px-6 pt-8 pb-32">
        <div className="flex items-center gap-1.5 text-[13px] text-gray-400 mb-1">
          <span>Projects</span>
          <ChevronRight className="w-3 h-3" />
          <span className="text-gray-700 font-medium">{breadcrumb}</span>
        </div>

        <div className="flex items-end justify-between mb-2">
          <h1 className="text-[28px] font-bold text-gray-900 tracking-tight">
            {project ? `${project.emoji} ${project.name}` : breadcrumb}
          </h1>
          {progress !== null && (
            <span className="text-sm text-gray-400 font-medium">{progress}% complete</span>
          )}
        </div>

        {nextTiny && (
          <div className="mb-6 mt-4 flex items-center gap-3 px-4 py-3 bg-amber-50 border border-amber-200/70 rounded-xl">
            <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
              <Zap className="w-4 h-4 text-amber-600" />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-semibold text-amber-600 uppercase tracking-wider">Your 2-Minute Tiny Start</p>
              <p className="text-sm text-gray-800 font-medium truncate">{nextTiny.title}</p>
            </div>
          </div>
        )}

        <div className="space-y-4 mt-4">
          {displayTasks.map(t => (
            <TaskCard
              key={t.id}
              task={t}
              projectId={activeProject ?? ""}
              projectColor={t._projectColor || projectColor}
              onToggleSubtask={toggleSubtask}
              onDeleteTask={deleteTask}
              onRemoveSubtask={removeSubtask}
            />
          ))}
        </div>

        {/* Trash view */}
        {activeFilter === "trash" ? (
          deletedTasks.length === 0 ? (
            <div className="text-center py-20 text-gray-400">
              <Trash2 className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm">Nothing in the trash.</p>
            </div>
          ) : (
            <div className="space-y-2 mt-4">
              {deletedTasks.map(d => (
                <div key={d.task.id} className="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl shadow-sm">
                  <span className="text-base">{d.projectEmoji}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-500 line-through truncate">{d.task.title}</p>
                    <p className="text-[11px] text-gray-400 mt-0.5">{d.projectName}</p>
                  </div>
                  <button
                    onClick={() => restoreTask(d.task.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-gray-600 hover:text-gray-900 bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 transition-all flex-shrink-0"
                  >
                    <RotateCcw className="w-3 h-3" /> Restore
                  </button>
                </div>
              ))}
            </div>
          )
        ) : (
          <>
            {displayTasks.length === 0 && (
              <div className="text-center py-20 text-gray-400">
                <Circle className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No tasks here yet.</p>
              </div>
            )}

            {/* Safety note — shown when viewing AI-generated plan */}
            {isAIPlan && planResponse && (
              <div className="mt-8 flex items-start gap-3 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl">
                <ShieldAlert className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
                <p className="text-[12px] text-gray-500 leading-relaxed">{planResponse.safety_note}</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
