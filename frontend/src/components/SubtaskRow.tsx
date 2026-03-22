import { Check, Zap } from "lucide-react";
import type { Subtask } from "../context/AppContext";

interface SubtaskRowProps {
  subtask: Subtask;
  onToggle: () => void;
  isNextStep: boolean;
}

export default function SubtaskRow({ subtask, onToggle, isNextStep }: SubtaskRowProps) {
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
      <span className={`flex-1 text-[14px] leading-snug ${
        subtask.done ? "line-through text-gray-400" : "text-gray-700"
      }`}>
        {subtask.title}
      </span>
      {isNextStep && !subtask.done && (
        <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 text-[11px] font-semibold rounded-md whitespace-nowrap">
          <Zap className="w-3 h-3" /> Start here
        </span>
      )}
    </div>
  );
}
