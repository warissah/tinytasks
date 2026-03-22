import { useState } from "react";
import { Brain, Timer, Coffee, Sparkles, ArrowRight } from "lucide-react";

interface OnboardingProps {
  onComplete: () => void;
}

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({ bigThing: "", time: "", style: "" });
  const [fadeClass, setFadeClass] = useState("opacity-100 translate-y-0");

  const goNext = () => {
    setFadeClass("opacity-0 translate-y-4");
    setTimeout(() => {
      setStep(s => s + 1);
      setFadeClass("opacity-0 -translate-y-4");
      setTimeout(() => setFadeClass("opacity-100 translate-y-0"), 50);
    }, 300);
  };

  const steps = [
    {
      icon: <Brain className="w-8 h-8" />,
      label: "Let's get unstuck.",
      question: "What's one big thing on your mind right now?",
      placeholder: "e.g. I need to find a new job...",
      field: "bigThing" as const,
    },
    {
      icon: <Timer className="w-8 h-8" />,
      label: "No pressure.",
      question: "How much time do you have today?",
      options: [
        { label: "15 min", emoji: "⚡", value: "15min" },
        { label: "30 min", emoji: "☕", value: "30min" },
        { label: "1 hour", emoji: "🎯", value: "1hr" },
        { label: "2+ hours", emoji: "🔥", value: "2hr+" },
      ],
      field: "time" as const,
    },
    {
      icon: <Coffee className="w-8 h-8" />,
      label: "Almost there.",
      question: "How do you like to work?",
      options: [
        { label: "Short bursts (5-15 min)", emoji: "⚡", value: "bursts" },
        { label: "Deep focus blocks", emoji: "🧘", value: "deep" },
        { label: "Mix of both", emoji: "🔀", value: "mix" },
      ],
      field: "style" as const,
    },
  ];

  if (step >= steps.length) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(249,250,251,0.97)", fontFamily: "'DM Sans', sans-serif" }}>
        <div className={`max-w-md text-center transition-all duration-500 ${fadeClass}`}>
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-8 h-8 text-emerald-500" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">You're all set.</h2>
          <p className="text-gray-500 mb-8 leading-relaxed">
            I've broken everything down into tiny steps.<br />
            Your first one will take less than 2 minutes.
          </p>
          <button
            onClick={onComplete}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-800 transition-colors"
          >
            Let's go <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  const current = steps[step];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(249,250,251,0.97)", fontFamily: "'DM Sans', sans-serif" }}>
      <div className={`max-w-lg w-full px-6 transition-all duration-300 ${fadeClass}`}>
        <div className="flex justify-center gap-2 mb-12">
          {steps.map((_, i) => (
            <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${i === step ? "w-8 bg-gray-900" : i < step ? "w-4 bg-gray-400" : "w-4 bg-gray-200"}`} />
          ))}
        </div>

        <div className="text-center">
          <div className="w-14 h-14 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-6 text-gray-600">
            {current.icon}
          </div>
          <p className="text-sm text-gray-400 font-medium mb-2">{current.label}</p>
          <h2 className="text-2xl font-semibold text-gray-900 mb-8">{current.question}</h2>

          {"placeholder" in current ? (
            <div>
              <input
                className="w-full px-5 py-4 rounded-xl border border-gray-200 bg-white text-gray-900 text-lg placeholder-gray-300 focus:outline-none focus:border-gray-400 focus:ring-0 transition-colors"
                placeholder={current.placeholder}
                value={answers[current.field]}
                onChange={e => setAnswers({ ...answers, [current.field]: e.target.value })}
                onKeyDown={e => e.key === "Enter" && answers[current.field] && goNext()}
                autoFocus
              />
              <button
                onClick={goNext}
                disabled={!answers[current.field]}
                className="mt-6 inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3 max-w-sm mx-auto">
              {current.options!.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => { setAnswers({ ...answers, [current.field]: opt.value }); goNext(); }}
                  className="flex items-center gap-4 px-5 py-4 rounded-xl border border-gray-200 bg-white hover:border-gray-400 hover:bg-gray-50 transition-all text-left group"
                >
                  <span className="text-xl">{opt.emoji}</span>
                  <span className="text-gray-700 font-medium group-hover:text-gray-900 transition-colors">{opt.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
