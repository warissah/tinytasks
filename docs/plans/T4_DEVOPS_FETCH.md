# T4 — DevOps, Fetch.ai (uAgents + Agentverse), Mongo Atlas, Vultr, demo

You make the **demo reliable**: deploy, secrets, **Fetch stack story**, and the **narrative** for judges.

**Load balancing — help the backend (T2):** After deploy exists, take point on **server env** (Mongo, Twilio, `INTERNAL_API_KEY`), **`curl`** verification of `/health` and `/internal/reminders/fire`, **CORS** for the production frontend origin, and **incident-style** debugging (502, wrong bind port, missing env). You do **not** own Pydantic schemas or core business logic unless T2 delegates a tiny, well-scoped task. You can also help **T1** with **`VITE_API_URL`** for prod and static build checks. Full table: **Load balancing** in [`../MASTER_PLAN.md`](../MASTER_PLAN.md).

## Fetch stack: how ASI:One, uAgents, and Agentverse fit **our** app

Read the full picture in [`../MASTER_PLAN.md`](../MASTER_PLAN.md) — sections **Fetch ecosystem** and **Strong integration story (Level B)**.

| Fetch piece | Your job (typical) |
|-------------|---------------------|
| **uAgents** | Implement the **proactive agent** that calls **`POST /internal/reminders/fire`** on a schedule or event. Pass optional **`agent_context`** (energy, push-back minutes, replan intensity) so **T2** can snooze/replan — **strong story**. |
| **Agentverse** | **Publish/register** that agent so judges see **discovery + deployment** in the Fetch ecosystem. |
| **ASI:One** | **Optional** for MVP: demo slide only, or a bonus path where ASI:One **invokes** your agent. **Do not** block shipping on ASI:One unless the track requires it. |

**Talk track:** **Gemini + FastAPI** = adaptive coaching copy and JSON plans; **uAgents + Agentverse** = proactive **agent** that triggers callbacks with structured metadata; **Twilio** = where users actually reply (“burnt out” → **webhook → T2**, not Fetch).

## Your mission

- **MongoDB Atlas**: cluster + connection string in `MONGODB_URI` (local `.env` only).
- **Vultr**: host FastAPI + static frontend (or split); public **HTTPS** URL required for Twilio + Fetch callbacks.
- **Fetch.ai (mandatory)**:
  - Build a **uAgent** (or equivalent per sponsor workshop) that **POST**s to `POST /internal/reminders/fire` with `X-Internal-Key` and JSON body — include **`agent_context`** when you want the **Level B** story (coordinate field names with **T2** / OpenAPI).
  - **Publish** the agent on **Agentverse** for the sponsor demo.
- **Demo**: 2-minute script + screen recording; show **Agentverse** + (if available) **ASI:One** slide.

## Where to work

- Root [`README.md`](../../README.md) — keep env table accurate.
- `backend/.env.example` — document every variable; no real values.
- Deployment notes: add `docs/DEPLOY.md` if helpful (optional).

## Fetch vs Gemini (talk track)

- **Gemini**: plan/nudge/replan **text** when **T2** calls the model.
- **uAgents**: **when** to trigger + optional **metadata** on the callback.
- **Agentverse**: where your agent is **visible** to the ecosystem.
- **ASI:One**: optional **assistant surface** — not your primary user path unless you add it.

## Testing

- **Integration**: from deployed URL, `curl` the internal endpoint with the secret; try **with and without** `agent_context` (see master plan JSON).
- **End-to-end**: uAgent fires → backend → Twilio sandbox message; Mongo shows updated **next reminder** if T2 implemented persistence.

## Checklist

- [ ] `INTERNAL_API_KEY` rotated if exposed; never committed.
- [ ] CORS updated for production frontend origin.
- [ ] Crisis disclaimer appears in web + WhatsApp copy.
- [ ] Agent **published** on Agentverse for judging.
- [ ] Callback uses **`agent_context`** at least once in demo if **Level B** is live.

See root [`README.md`](../../README.md).
