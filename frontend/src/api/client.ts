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
  user_id?: string;
  phone?: string;
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

export type CreateGuestUserRequest = {
  email: string;
  phone: string;
};

export type CreateGuestUserResponse = {
  user_id: string;
  email: string;
  phone: string;
  is_new_user: boolean;
  persistence: "mongo" | "demo_fallback";
};

export async function postGuestUser(body: CreateGuestUserRequest): Promise<CreateGuestUserResponse> {
  const res = await fetch(`${baseUrl}/users/guest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST /users/guest failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<CreateGuestUserResponse>;
}

export type NudgeRequest = {
  task_id: string;
  context: string;
  last_step_id?: string;
};

export type NudgeResponse = {
  nudge_type: string;
  message: string;
  two_minute_action: string;
};

export async function postNudge(body: NudgeRequest): Promise<NudgeResponse> {
  const res = await fetch(`${baseUrl}/nudge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST /nudge failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<NudgeResponse>;
}

export async function postSessionStart(task_id: string): Promise<void> {
  await fetch(`${baseUrl}/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id, started_at: new Date().toISOString() }),
  });
}

export type DemoEvent =
  | { id: string; type: "task_complete"; data: Record<string, never>; timestamp: number }
  | { id: string; type: "nudge"; data: { message: string; two_minute_action: string }; timestamp: number }
  | { id: string; type: "new_plan"; data: { plan: PlanResponse; goal: string }; timestamp: number };

export async function getDemoEvents(since?: number): Promise<DemoEvent[]> {
  const url = since != null
    ? `${baseUrl}/demo/events?since=${since}`
    : `${baseUrl}/demo/events`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const json = await res.json() as { events: DemoEvent[] };
  return json.events ?? [];
}

export async function postSessionEnd(
  task_id: string,
  reflection: "done" | "blocked" | "partial"
): Promise<void> {
  await fetch(`${baseUrl}/session/end`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id, ended_at: new Date().toISOString(), reflection }),
  });
}
