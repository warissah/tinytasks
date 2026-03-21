import { useEffect, useState } from "react";
import { getHealth, postPlan, type PlanResponse } from "./api/client";
import "./App.css";

export default function App() {
  const [health, setHealth] = useState<string>("loading…");
  const [goal, setGoal] = useState("Ship a vertical slice for the hackathon");
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((h) => setHealth(h.status))
      .catch((e: unknown) => setHealth(e instanceof Error ? e.message : "error"));
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setPlan(null);
    try {
      const p = await postPlan({
        goal,
        horizon: "today",
        available_minutes: 90,
        energy: "medium",
      });
      setPlan(p);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>ADHD execution coach</h1>
        <p className="muted">
          Barebones template — replace stub plans with Gemini. Not a clinical service.
        </p>
        <p className="badge">API health: {health}</p>
      </header>

      <main className="main">
        <form className="card" onSubmit={onSubmit}>
          <label className="label">
            Goal
            <textarea
              className="input"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              rows={3}
            />
          </label>
          <button className="button" type="submit">
            Get stub plan
          </button>
          {error ? <pre className="error">{error}</pre> : null}
        </form>

        {plan ? (
          <section className="card">
            <h2>Plan (stub)</h2>
            <p>{plan.summary}</p>
            <h3>Tiny first step</h3>
            <p>
              <strong>{plan.tiny_first_step.title}</strong> —{" "}
              {plan.tiny_first_step.description} (~{plan.tiny_first_step.estimated_minutes} min)
            </p>
            <h3>Steps</h3>
            <ol>
              {plan.steps.map((s) => (
                <li key={s.id}>
                  <strong>{s.title}</strong> — {s.description} (~{s.estimated_minutes} min)
                </li>
              ))}
            </ol>
            <h3>If / then</h3>
            <p>
              If {plan.implementation_intention.if_condition}, then{" "}
              {plan.implementation_intention.then_action}.
            </p>
            <p className="safety">{plan.safety_note}</p>
          </section>
        ) : null}
      </main>
    </div>
  );
}
