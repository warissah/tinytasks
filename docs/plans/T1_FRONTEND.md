# T1 — Frontend (Vite + React + TypeScript)

You own everything the **browser** sees. The API contract is defined in [`../MASTER_PLAN.md`](../MASTER_PLAN.md); backend implements it under `backend/app/schemas/`.

**Load balancing:** **T3** can help you with extra UI (e.g. a simple **“Stuck”** box calling `POST /nudge`), loading/error copy, or a second pass on state. See **Load balancing** in [`../MASTER_PLAN.md`](../MASTER_PLAN.md). **T4** can help with **production `VITE_API_URL`** (points at **Render** backend URL), **Vercel** deploy, build/preview, and smoke tests.

## Your mission

- **Goal** screen: collect `goal`, `horizon`, `available_minutes`, `energy` → `POST /plan`.
- **Plan** screen: render `tiny_first_step`, `steps[]`, `implementation_intention`, `safety_note`.
- **Session** screen: start/end session → `POST /session/start`, `POST /session/end` (wire when backend persists).
- Loading, empty, and error states (don’t block on “pretty” — block on **clear**).

**Stretch (optional):** A **chat** UI calling **`POST /chat/message`** and **`POST /chat/finalize`** (OpenAPI `/docs`) if T2 has it enabled. **Skipping chat is OK** — judges still see the form → plan path. Coordinate with T2; don’t let chat block the MVP checklist below.

## Where to work

- `frontend/src/` — components, pages, API client.
- `frontend/.env.local` — set `VITE_API_URL` (see `frontend/.env.example`). **Never commit secrets.**

## Contracts

- Use `fetch` or `axios` against `import.meta.env.VITE_API_URL`.
- Prefer **one TypeScript type** mirroring the plan response (copy fields from OpenAPI at `/openapi.json` later, or hand-maintain).

## Learning path (barebones repo is intentional)

- Add React Router if you want multiple URLs.
- Add `openapi-typescript` to generate types from FastAPI when T2 stabilizes `/openapi.json`.

## Checklist before integration freeze

- [ ] `npm run dev` loads and shows health + stub plan from API.
- [ ] Errors from API show a readable message (even raw JSON in `<pre>` is OK for MVP).
- [ ] Crisis / non-clinical disclaimer visible when displaying AI output.

## Testing (your responsibility)

- **Unit**: Vitest — test pure formatters and small components with mocked `fetch`.
- **Integration (manual)**: with backend running, click through goal → plan; verify network tab shows 200 on `/plan`.

See root [`README.md`](../../README.md) for commands.
