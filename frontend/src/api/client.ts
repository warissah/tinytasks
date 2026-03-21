/** Default matches local FastAPI; override with `VITE_API_URL` in `.env.local` for deploy. */
const baseUrl = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch(`${baseUrl}/health`);
  if (!res.ok) {
    throw new Error(`GET /health failed: ${res.status}`);
  }
  return res.json() as Promise<{ status: string }>;
}

export type PlanRequest = {
  goal: string;
  horizon: "today" | "week" | "long";
  available_minutes: number;
  energy: "low" | "medium" | "high";
};

export type PlanResponse = {
  plan_id: string;
  summary: string;
  tiny_first_step: {
    title: string;
    description: string;
    estimated_minutes: number;
  };
  steps: Array<{
    id: string;
    title: string;
    description: string;
    estimated_minutes: number;
  }>;
  implementation_intention: {
    if_condition: string;
    then_action: string;
  };
  safety_note: string;
};

export async function postPlan(body: PlanRequest): Promise<PlanResponse> {
  const res = await fetch(`${baseUrl}/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST /plan failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<PlanResponse>;
}
