# BeachHacks — ADHD execution coach

**Team 41 · BeachHack 9.0** — [GitHub repo](https://github.com/warissah/tinytasks)

**FastAPI** + **Vite/React** monorepo. **Architecture, roles, and hackathon planning** live under [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md) and [`docs/plans/`](docs/plans/) (T1–T4).

## Quick start (no API keys required)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: edit later for real keys
uvicorn app.main:app --reload --port 8000
```

- Health: <http://127.0.0.1:8000/health>
- OpenAPI: <http://127.0.0.1:8000/docs>

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # default points API at http://127.0.0.1:8000
npm run dev
```

Open the printed local URL (usually <http://127.0.0.1:5173>).

## Environment variables

**Do not commit real keys.** Copy examples and fill locally:

| File | Purpose |
|------|---------|
| [`backend/.env.example`](backend/.env.example) | Server + internal webhook secret + Mongo + Gemini (`google-genai`) + Twilio |
| [`frontend/.env.example`](frontend/.env.example) | `VITE_API_URL` for browser → FastAPI |

## Testing

### Unit tests (fast, no network)

**Backend (pytest)** — logic and request/response shape without requiring a real MongoDB or external APIs:

```bash
cd backend
source .venv/bin/activate
pytest
```

- Tests live in `backend/tests/`.
- Prefer **pure functions** and **Pydantic models** for anything you want easy unit coverage.

**Frontend (Vitest)** — components and small modules in isolation:

```bash
cd frontend
npm run test
```

### Integration tests (API contract)

**Backend integration** uses FastAPI’s `TestClient` to hit the real app in-process (Twilio/Mongo/Gemini still optional depending on `.env`):

```bash
cd backend
pytest -m integration
```

Run everything including integration-marked tests:

```bash
pytest
```

The `integration` marker is defined in [`backend/pytest.ini`](backend/pytest.ini).

### Manual end-to-end (recommended before judging)

1. Terminal A: from `backend/`, run `uvicorn app.main:app --reload --port 8000`.
2. Terminal B: from `frontend/`, run `npm run dev`.
3. Confirm the UI shows **healthy** and a **plan** response from the API (stub if `GEMINI_API_KEY` is unset; otherwise Gemini).

For **WhatsApp / Fetch / Mongo**: add keys to `backend/.env`, then repeat and point Twilio sandbox + Fetch callbacks at your **deployed HTTPS** URL.

**Production deploy (team default):** **Railway** for `backend/` (HTTPS). **Vercel** for `frontend/`; set **`VITE_API_URL`** to the Railway API origin. Add your Vercel URL(s) to backend **`CORS_ORIGINS`** on Railway. Details: [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md) and [`docs/plans/T4_DEVOPS_FETCH.md`](docs/plans/T4_DEVOPS_FETCH.md).

## Integration contract (frozen for the hackathon)

- Browser → `VITE_API_URL` (see [`frontend/.env.example`](frontend/.env.example)).
- FastAPI enables CORS for local dev; in production include your **Vercel** origin(s) in **`CORS_ORIGINS`**.
- `POST /plan` returns the shared JSON shape; see [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md).

## Repo layout

```
backend/          FastAPI app, Pydantic schemas, routers, pytest
frontend/         Vite + React + TypeScript
docs/             Master plan + per-role playbooks (T1–T4)
```

