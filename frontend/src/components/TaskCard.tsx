import { useState, useRef, useEffect } from "react";
import { Check, AlertCircle, Clock, ChevronDown, ChevronRight, MoreHorizontal, Trash2 } from "lucide-react";
import type { Task } from "../context/AppContext";
import SubtaskRow from "./SubtaskRow";

interface TaskCardProps {
  task: Task;
  projectId: string;
  projectColor: string;
  onToggleSubtask: (taskId: string, subtaskId: string) => void;
  onDeleteTask: (projectId: string, taskId: string) => void;
  onRemoveSubtask: (projectId: string, taskId: string, subtaskId: string) => void;
}

export default function TaskCard({ task, projectId, projectColor, onToggleSubtask, onDeleteTask, onRemoveSubtask }: TaskCardProps) {
  const [open, setOpen] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const doneCount = task.subtasks?.filter(s => s.done).length || 0;
  const totalCount = task.subtasks?.length || 0;
  const progress = totalCount > 0 ? (doneCount / totalCount) * 100 : 0;
  const nextStep = task.subtasks?.find(s => !s.done);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="bg-white rounded-2xl border border-gray-200/80 shadow-sm hover:shadow-md transition-shadow">
      <div className="px-5 pt-5 pb-3">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="mt-0.5">
              {task.done
                ? <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center"><Check className="w-3.5 h-3.5 text-white" strokeWidth={3} /></div>
                : <div className="w-6 h-6 rounded-full border-2 border-gray-300" />
              }
            </div>
            <div className="min-w-0">
              <h3 className={`font-medium text-[15px] leading-tight ${task.done ? "line-through text-gray-400" : "text-gray-600"}`}>
                {task.title}
              </h3>
              <div className="flex items-center gap-3 mt-1.5">
                {task.urgent && (
                  <span className="flex items-center gap-1 text-[11px] font-semibold text-red-500">
                    <AlertCircle className="w-3 h-3" /> Urgent
                  </span>
                )}
                {task.timeEstimate && (
                  <span className="flex items-center gap-1 text-[11px] text-gray-400">
                    <Clock className="w-3 h-3" /> {task.timeEstimate}
                  </span>
                )}
                <span className="text-[11px] text-gray-400">{doneCount}/{totalCount} steps</span>
              </div>
            </div>
          </div>

          {/* 3-dot menu */}
          <div className="relative flex-shrink-0" ref={menuRef}>
            <button
              onClick={() => setMenuOpen(o => !o)}
              className="p-1 rounded-md hover:bg-gray-100 transition-colors"
            >
              <MoreHorizontal className="w-4 h-4 text-gray-400" />
            </button>
            {menuOpen && (
              <div className="absolute right-0 top-7 z-50 w-40 bg-white border border-gray-200 rounded-xl shadow-lg py-1">
                <button
                  onClick={() => { onDeleteTask(projectId, task.id); setMenuOpen(false); }}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete task
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%`, backgroundColor: progress === 100 ? "#10B981" : projectColor || "#6366F1" }}
          />
        </div>
      </div>

      {task.subtasks && task.subtasks.length > 0 && (
        <div className="px-5 pb-4">
          <button
            onClick={() => setOpen(o => !o)}
            className="flex items-center gap-1.5 text-[12px] font-medium text-gray-400 hover:text-gray-600 transition-colors py-1.5"
          >
            {open ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            Subtasks
          </button>
          {open && (
            <div className="mt-1 space-y-0.5 ml-1">
              {task.subtasks.map(s => (
                <SubtaskRow
                  key={s.id}
                  subtask={s}
                  isNextStep={nextStep?.id === s.id}
                  onToggle={() => onToggleSubtask(task.id, s.id)}
                  onDelete={() => onRemoveSubtask(projectId, task.id, s.id)}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
