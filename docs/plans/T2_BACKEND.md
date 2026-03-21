# T2 — Backend (FastAPI + Pydantic)

You own **API correctness**, **JSON schemas**, and **calling Gemini** (via OpenClaw or direct Google SDK). WhatsApp and Fetch call **your** routes — they should not reimplement business logic.

## Your mission

- Replace **stub** `POST /plan` with real Gemini output that validates against Pydantic models.
- Implement `POST /nudge`, session routes, Mongo persistence.
- Secure `POST /internal/reminders/fire` with `X-Internal-Key` (see `backend/app/config.py`).
- Keep **one source of truth** for schemas in `backend/app/schemas/`.

## Where to work

- `backend/app/main.py` — app factory, CORS, router includes.
- `backend/app/routers/` — one file per area (`plan.py`, `nudge.py`, `session.py`, `internal_reminders.py`, `webhooks_twilio.py`).
- `backend/app/schemas/` — Pydantic models shared by all routes.

## Environment

- Copy `backend/.env.example` → `backend/.env`. **Do not commit `.env`.**
- For local dev, stub routes work **without** Gemini until you add keys.

## Gemini / OpenClaw

- Return **JSON-only** from the model; validate with Pydantic; on failure, one repair retry.
- Log errors without leaking user content to console in production.

## Checklist

- [ ] `/docs` (Swagger) lists all routes.
- [ ] `POST /plan` response matches the master plan JSON shape.
- [ ] Internal route returns 401/403 if key missing.

## Testing (your responsibility)

- **Unit**: pure functions (prompt building, parsing) + schema validation.
- **Integration**: `TestClient` tests in `backend/tests/` hitting `/health`, `/plan`, `/internal/reminders/fire`.

See root [`README.md`](../../README.md) for pytest commands.
