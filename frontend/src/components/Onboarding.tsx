import { useState } from "react";
import { Brain, Timer, Coffee, Sparkles, ArrowRight, Mail, Phone } from "lucide-react";
import { postGuestUser, postPlan } from "../api/client";
import type { PlanResponse } from "../api/client";
import { storeGuestUser } from "../utils/guestUser";

interface OnboardingProps {
  onComplete: (plan: PlanResponse, goal: string, email: string, phone: string) => void;
}

const TIME_TO_MINUTES: Record<string, number> = {
  "15min": 15,
  "30min": 30,
  "1hr": 60,
  "2hr+": 120,
};

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({ email: "", phone: "", goal: "", time: "", energy: "" });
  const [fadeClass, setFadeClass] = useState("opacity-100 translate-y-0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const goNext = () => {
    setFadeClass("opacity-0 translate-y-4");
    setTimeout(() => {
      setStep(s => s + 1);
      setFadeClass("opacity-0 -translate-y-4");
      setTimeout(() => setFadeClass("opacity-100 translate-y-0"), 50);
    }, 300);
  };

  const handleSubmit = async (finalAnswers: typeof answers) => {
    setLoading(true);
    setError(null);
    try {
      const guestUser = await postGuestUser({
        email: finalAnswers.email,
        phone: finalAnswers.phone,
      });
      storeGuestUser(guestUser);
      const { user_id, phone } = guestUser;
      const plan = await postPlan({
        goal: finalAnswers.goal,
        horizon: "today",
        available_minutes: TIME_TO_MINUTES[finalAnswers.time] ?? 30,
        energy: finalAnswers.energy as "low" | "medium" | "high",
        user_id,
        phone,
      });
      onComplete(plan, finalAnswers.goal, guestUser.email, guestUser.phone);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  const steps = [
    {
      icon: <Mail className="w-8 h-8" />,
      label: "Welcome to TinyTasks.",
      question: "What's your email address?",
      placeholder: "you@example.com",
      field: "email" as const,
      validate: (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
    },
    {
      icon: <Phone className="w-8 h-8" />,
      label: "Stay connected.",
      question: "What's your WhatsApp number?",
      placeholder: "+1 (555) 000-0000",
      field: "phone" as const,
      validate: (v: string) => /^\+?[\d\s\-().]{7,}$/.test(v),
    },
    {
      icon: <Brain className="w-8 h-8" />,
      label: "Let's get unstuck.",
      question: "What's one big thing on your mind right now?",
      placeholder: "e.g. I need to finish my resume...",
      field: "goal" as const,
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
      question: "How's your energy level right now?",
      options: [
        { label: "Low — need small steps", emoji: "🌙", value: "low" },
        { label: "Medium — ready to work", emoji: "⚡", value: "medium" },
        { label: "High — let's go!", emoji: "🔥", value: "high" },
      ],
      field: "energy" as const,
    },
  ];

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: "rgba(249,250,251,0.97)", fontFamily: "'DM Sans', sans-serif" }}>
        <div className="max-w-md text-center">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-8 h-8 text-gray-600 animate-pulse" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Building your plan...</h2>
          <p className="text-gray-400 text-sm">Breaking your goal into tiny, manageable steps.</p>
          {error && (
            <div className="mt-6">
              <p className="text-red-500 text-sm mb-4">{error}</p>
              <button
                onClick={() => handleSubmit(answers)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-800 transition-colors"
              >
                Try again <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
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
                type={current.field === "email" ? "email" : current.field === "phone" ? "tel" : "text"}
                value={answers[current.field]}
                onChange={e => setAnswers({ ...answers, [current.field]: e.target.value })}
                onKeyDown={e => {
                  const valid = "validate" in current ? current.validate!(answers[current.field]) : !!answers[current.field];
                  if (e.key === "Enter" && valid) goNext();
                }}
                autoFocus
              />
              <button
                onClick={goNext}
                disabled={"validate" in current ? !current.validate!(answers[current.field]) : !answers[current.field]}
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
                  onClick={() => {
                    const newAnswers = { ...answers, [current.field]: opt.value };
                    setAnswers(newAnswers);
                    if (step < steps.length - 1) {
                      goNext();
                    } else {
                      handleSubmit(newAnswers);
                    }
                  }}
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
