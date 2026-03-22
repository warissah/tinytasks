import { useState, useEffect } from "react";
import { Brain, Send, Sparkles, Plus } from "lucide-react";
import { postNudge } from "../api/client";
import { useAppContext } from "../context/AppContext";

export default function AIChatInput() {
  const { planResponse, activeProject, projects, addSubtask, whatsAppNudge, clearWhatsAppNudge } = useAppContext();
  const [value, setValue] = useState("");
  const [expanded, setExpanded] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [response, setResponse] = useState<{ message: string; two_minute_action: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [subtaskAdded, setSubtaskAdded] = useState(false);
  const [isWhatsApp, setIsWhatsApp] = useState(false);

  // Auto-display nudge when it arrives from WhatsApp
  useEffect(() => {
    if (!whatsAppNudge) return;
    setResponse({ message: whatsAppNudge.message, two_minute_action: whatsAppNudge.two_minute_action });
    setExpanded(true);
    setIsWhatsApp(true);
    setSubtaskAdded(false);
  }, [whatsAppNudge]);

  // Find the first incomplete task in the active project
  const activeTask = (() => {
    if (!activeProject) return null;
    const proj = projects.find(p => p.id === activeProject);
    return proj?.tasks.find(t => !t.done) ?? null;
  })();
  const activeTaskId = activeTask?.id ?? null;

  // Build a rich context string so Gemini knows what the user is working on
  const buildContext = (userMessage: string): string => {
    const parts: string[] = [];
    if (activeTask) {
      parts.push(`Task: ${activeTask.title}`);
      const remaining = activeTask.subtasks?.filter(s => !s.done) ?? [];
      const done = activeTask.subtasks?.filter(s => s.done) ?? [];
      if (remaining.length > 0) {
        parts.push(`Remaining steps: ${remaining.map(s => s.title).join(", ")}`);
      }
      if (done.length > 0) {
        parts.push(`Completed steps: ${done.map(s => s.title).join(", ")}`);
      }
      const nextStep = remaining[0];
      if (nextStep) parts.push(`Next step: ${nextStep.title}${nextStep.description ? ` — ${nextStep.description}` : ""}`);
    }
    parts.push(`User says: ${userMessage}`);
    return parts.join("\n");
  };

  const handleSubmit = async () => {
    if (!value.trim()) return;
    setThinking(true);
    setExpanded(true);
    setError(null);
    setResponse(null);
    setSubtaskAdded(false);

    try {
      const nudge = await postNudge({
        task_id: planResponse?.plan_id ?? activeTaskId ?? "unknown",
        context: buildContext(value.trim()),
      });
      setResponse({ message: nudge.message, two_minute_action: nudge.two_minute_action });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't reach the coach. Try again.");
    } finally {
      setThinking(false);
    }
  };

  const handleAddSubtask = () => {
    if (!response?.two_minute_action || !activeProject || !activeTaskId) return;
    addSubtask(activeProject, activeTaskId, response.two_minute_action);
    setSubtaskAdded(true);
  };

  const handleDismiss = () => {
    setExpanded(false);
    setResponse(null);
    setError(null);
    setSubtaskAdded(false);
    setIsWhatsApp(false);
    setValue("");
    clearWhatsAppNudge();
  };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30 w-full max-w-xl px-4">
      {expanded && (thinking || response || error) && (
        <div className="mb-3 bg-white/90 backdrop-blur-xl border border-gray-200 rounded-2xl shadow-lg p-5" style={{ fontFamily: "'DM Sans', sans-serif" }}>
          {thinking ? (
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
              Breaking that down for you...
            </div>
          ) : error ? (
            <div>
              <p className="text-sm text-red-500">{error}</p>
              <button onClick={handleDismiss} className="mt-3 text-[12px] text-gray-400 hover:text-gray-600 transition-colors">Dismiss</button>
            </div>
          ) : response && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-md bg-gray-900 flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-900">Coach</span>
                {isWhatsApp && (
                  <span className="text-[10px] font-medium text-green-600 bg-green-50 border border-green-200 px-1.5 py-0.5 rounded-md ml-1">via WhatsApp</span>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-3">{response.message}</p>
              {response.two_minute_action && (
                <div className="bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 mb-3">
                  <p className="text-[11px] font-semibold text-amber-600 uppercase tracking-wider mb-1">2-Minute Action</p>
                  <p className="text-sm text-gray-700">{response.two_minute_action}</p>
                  {activeProject && activeTaskId && (
                    <button
                      onClick={handleAddSubtask}
                      disabled={subtaskAdded}
                      className="mt-2 flex items-center gap-1.5 text-[12px] font-medium text-amber-700 hover:text-amber-900 disabled:opacity-50 transition-colors"
                    >
                      <Plus className="w-3 h-3" />
                      {subtaskAdded ? "Added to task ✓" : "Add as subtask"}
                    </button>
                  )}
                </div>
              )}
              <button onClick={handleDismiss} className="text-[12px] text-gray-400 hover:text-gray-600 transition-colors">Dismiss</button>
            </div>
          )}
        </div>
      )}

      <div className="bg-white/85 backdrop-blur-xl border border-gray-200/80 rounded-2xl shadow-lg flex items-center gap-2 px-4 py-3" style={{ fontFamily: "'DM Sans', sans-serif" }}>
        <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
          <Brain className="w-4 h-4 text-gray-500" />
        </div>
        <input
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSubmit()}
          placeholder="Tell me what's blocking you..."
          className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 focus:outline-none"
        />
        <button
          onClick={handleSubmit}
          disabled={!value.trim()}
          className="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center text-white hover:bg-gray-800 disabled:opacity-20 disabled:cursor-not-allowed transition-all flex-shrink-0"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
