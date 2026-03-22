# T2 — Backend (FastAPI + Pydantic)

You own **API correctness**, **JSON schemas**, and **calling Gemini** with the official **`google-genai`** SDK (`GEMINI_API_KEY`). WhatsApp and Fetch call **your** routes — they should not reimplement business logic. **OpenClaw is out of scope** for this team (direct Gemini keeps deploy and debugging simpler).

**Load balancing:** **T4** can take work off your plate for **deploy-only** issues: env vars on the server, `curl` checks for `/internal/reminders/fire`, CORS against the real site URL, and documenting URLs for webhooks. You still own schemas and core route behavior. See **Load balancing** in [`../MASTER_PLAN.md`](../MASTER_PLAN.md).

## Your mission

- Replace **stub** `POST /plan` with real Gemini output that validates against Pydantic models.
- Implement `POST /nudge`, session routes, Mongo persistence.
- Secure `POST /internal/reminders/fire` with `X-Internal-Key` (see `backend/app/config.py`).
- **Strong integration (Level B):** When the Fetch **uAgent** calls `/internal/reminders/fire`, accept optional **`agent_context`** (`energy_hint`, `push_back_start_minutes`, `replan_intensity`). Load task/user from **Mongo**, merge with last **WhatsApp** state, then: update **next nudge time**, call **Gemini** to **subdivide or soften** the plan when `replan_intensity` is `smaller_steps` / `lighter`, send outbound line via **Twilio**. See [`../MASTER_PLAN.md`](../MASTER_PLAN.md) (sections **Fetch ecosystem** and **Strong integration story**).
- Keep **one source of truth** for schemas in `backend/app/schemas/` (including `app/schemas/internal.py` for `AgentCallbackContext`).

## Where to work

- `backend/app/main.py` — app factory, CORS, router includes.
- `backend/app/routers/` — one file per area (`plan.py`, `nudge.py`, `session.py`, `internal_reminders.py`, `webhooks_twilio.py`).
- `backend/app/schemas/` — Pydantic models shared by all routes.

## Environment

- Copy `backend/.env.example` → `backend/.env`. **Do not commit `.env`.**
- For local dev, stub routes work **without** Gemini until you add keys.

## Gemini (`google-genai`)

- Use **`google.genai`** / `Client` with **`GEMINI_API_KEY`** — see [Google Gen AI SDK (Python)](https://googleapis.github.io/python-genai/).
- Return **JSON-only** from the model; validate with Pydantic; on failure, one repair retry (“fix JSON only”).
- Log errors without leaking user content to console in production.

### Time constraints (24h) — scope Gemini “sophistication”

Ship the **vertical slice** first; add polish only if the core path works.

1. **Must ship:** One **system prompt + user payload** per feature (`/plan`, `/nudge`, replan inside `/internal/reminders/fire`) that returns **valid JSON** matching existing Pydantic models. Stub fallback when `GEMINI_API_KEY` is missing stays OK for local dev.
2. **Nice if time:** Separate prompt helpers per `energy` / `replan_intensity`, slightly richer instructions, or a second model name for “lighter” copy — **after** Mongo + one happy-path Gemini call works end-to-end.
3. **Defer:** Multi-turn coaching, long chat history, many model variants, or anything that needs more than **one request + validation + one retry** per endpoint.

**Rule:** A **reliable** JSON plan + one replan path beats a **clever** prompt that breaks under judge Wi‑Fi.

## Checklist

- [ ] `/docs` (Swagger) lists all routes.
- [ ] `POST /plan` response matches the master plan JSON shape.
- [ ] Internal route returns 401/403 if key missing.

## Testing (your responsibility)

- **Unit**: pure functions (prompt building, parsing) + schema validation.
- **Integration**: `TestClient` tests in `backend/tests/` hitting `/health`, `/plan`, `/internal/reminders/fire`.

See root [`README.md`](../../README.md) for pytest commands.
