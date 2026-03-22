import { useState } from "react";
import { Brain, Send, Sparkles } from "lucide-react";

export default function AIChatInput() {
  const [value, setValue] = useState("");
  const [expanded, setExpanded] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [response, setResponse] = useState<{ text: string; steps: string[] } | null>(null);

  const handleSubmit = () => {
    if (!value.trim()) return;
    setThinking(true);
    setExpanded(true);
    setTimeout(() => {
      setThinking(false);
      setResponse({
        text: "Let's break that down. Here's what I'd suggest:",
        steps: [
          "Open a blank doc — just title it for now (1 min)",
          "Write one sentence about what you want to say (1 min)",
          "List 3 bullet points of key ideas (2 min)",
          "Expand each bullet into a short paragraph (5 min)",
        ],
      });
    }, 2000);
  };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30 w-full max-w-xl px-4">
      {expanded && (thinking || response) && (
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
          ) : response && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-md bg-gray-900 flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-900">Coach</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{response.text}</p>
              <div className="space-y-2">
                {response.steps.map((step, i) => (
                  <div key={i} className="flex items-start gap-2.5 text-sm">
                    <span className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-[11px] font-semibold text-gray-500 flex-shrink-0 mt-0.5">{i + 1}</span>
                    <span className="text-gray-700">{step}</span>
                  </div>
                ))}
              </div>
              <button
                onClick={() => { setExpanded(false); setResponse(null); setValue(""); }}
                className="mt-4 text-[12px] text-gray-400 hover:text-gray-600 transition-colors"
              >
                Dismiss
              </button>
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
