# BeachHacks — ADHD execution coach (hackathon starter)

**Team 41 · BeachHack 9.0** — [GitHub repo](https://github.com/warissah/beachhack9.0--team41--project)

Barebones **FastAPI** + **Vite/React** monorepo: API contract, CORS, and stub routes are wired so the team can run **backend + frontend together** before any real API keys. Product plans live under [`docs/`](docs/).

## Documentation

| Doc | Audience |
|-----|----------|
| [`docs/MASTER_PLAN.md`](docs/MASTER_PLAN.md) | Whole team — architecture, JSON API, 24h schedule |
| [`docs/plans/T1_FRONTEND.md`](docs/plans/T1_FRONTEND.md) | Frontend (Vite + React) |
| [`docs/plans/T2_BACKEND.md`](docs/plans/T2_BACKEND.md) | Backend (FastAPI, Gemini, Mongo) |
| [`docs/plans/T3_WHATSAPP.md`](docs/plans/T3_WHATSAPP.md) | WhatsApp / Twilio |
| [`docs/plans/T4_DEVOPS_FETCH.md`](docs/plans/T4_DEVOPS_FETCH.md) | DevOps, Fetch.ai, deploy, demo |

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

Open the printed local URL (usually <http://127.0.0.1:5173>). The home page calls `GET /health` and `POST /plan` (stub).

## Environment variables

**Do not commit real keys.** Copy examples and fill locally:

| File | Purpose |
|------|---------|
| [`backend/.env.example`](backend/.env.example) | Server + internal webhook secret + future Twilio/Mongo/Gemini/Fetch |
| [`frontend/.env.example`](frontend/.env.example) | `VITE_API_URL` for browser → FastAPI |

## Testing

### Unit tests (fast, no network)

**Backend (pytest)** — logic and request/response shape without running a real DB or external APIs:

```bash
cd backend
source .venv/bin/activate
pytest
```

- Tests live in `backend/tests/`.
- Use **pure functions** and **Pydantic models** for anything you want easy unit coverage.

**Frontend (Vitest)** — components and small modules in isolation:

```bash
cd frontend
npm run test
```

### Integration tests (API contract)

**Backend integration** uses FastAPI’s `TestClient` to hit the real app stack in-process (still no Twilio/Mongo if not configured):

```bash
cd backend
pytest -m integration
```

Run all tests including integration:

```bash
pytest
```

(`integration` marker is optional; see `backend/pytest.ini`.)

### Manual end-to-end (recommended before judging)

1. Terminal A: `uvicorn app.main:app --reload --port 8000` from `backend/`
2. Terminal B: `npm run dev` from `frontend/`
3. Confirm UI shows **healthy** and **stub plan** JSON.

For WhatsApp/Fetch/Mongo: add keys to `backend/.env`, then repeat and use Twilio sandbox + Fetch callback URL against your deployed HTTPS URL.

## Repo layout

```
backend/          FastAPI app, Pydantic schemas, routers, pytest
frontend/         Vite + React + TypeScript
docs/             Master plan + per-role plans
```

## Integration contract (frozen for the hackathon)

- Browser → `VITE_API_URL` (see `frontend/.env.example`).
- FastAPI enables CORS for local dev origins; tighten for production.
- `POST /plan` returns the shared JSON shape (stub until Gemini is wired); see `docs/MASTER_PLAN.md`.

## License

Hackathon project — set license as your team prefers.
