import { Check, Zap, X } from "lucide-react";
import type { Subtask } from "../context/AppContext";

interface SubtaskRowProps {
  subtask: Subtask;
  onToggle: () => void;
  onDelete: () => void;
  isNextStep: boolean;
}

export default function SubtaskRow({ subtask, onToggle, onDelete, isNextStep }: SubtaskRowProps) {
  return (
    <div
      className={`group flex items-center gap-3 py-2.5 px-3 rounded-lg transition-all ${
        isNextStep && !subtask.done ? "bg-amber-50/70 border border-amber-200/60" : "hover:bg-gray-50"
      }`}
    >
      <button onClick={onToggle} className="flex-shrink-0 relative">
        {subtask.done ? (
          <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
            <Check className="w-3 h-3 text-white" strokeWidth={3} />
          </div>
        ) : (
          <div className={`w-5 h-5 rounded-full border-2 transition-colors ${
            isNextStep ? "border-amber-400 hover:border-amber-500" : "border-gray-300 hover:border-gray-400"
          }`} />
        )}
      </button>
      <div className="flex-1 min-w-0">
        <span className={`text-[14px] leading-snug font-medium ${
          subtask.done ? "line-through text-gray-400 font-normal" : "text-gray-800"
        }`}>
          {subtask.title}
        </span>
        {subtask.description && !subtask.done && (
          <p className="text-[12px] text-gray-400 leading-snug mt-0.5">{subtask.description}</p>
        )}
      </div>
      {isNextStep && !subtask.done && (
        <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 text-[11px] font-semibold rounded-md whitespace-nowrap">
          <Zap className="w-3 h-3" /> Start here
        </span>
      )}
      <button
        onClick={onDelete}
        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-200 transition-all flex-shrink-0"
        title="Remove step"
      >
        <X className="w-3 h-3 text-gray-400" />
      </button>
    </div>
  );
}
