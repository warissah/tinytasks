# T3 — WhatsApp (Twilio)

You own **inbound** webhooks and **outbound** messages. Business logic stays in **T2’s** services — you **call the same endpoints** the web app uses (or thin wrappers), so behavior stays consistent.

**Load balancing — help the frontend (T1):** If WhatsApp integration is slow, help **T1** ship a minimal **in-app “Stuck”** flow (input + submit) that hits **`POST /nudge`** so the demo still shows anti-procrastination behavior in the browser. You can also pair on error/loading UI and copy. Details: **Load balancing** in [`../MASTER_PLAN.md`](../MASTER_PLAN.md).

**Fetch vs WhatsApp:** User messages (“I’m burnt out”, “stuck”) arrive via **Twilio → this backend**, not through the Fetch uAgent. **T2** persists mood/snooze flags in **Mongo** so the **next** uAgent callback + **`agent_context`** (or backend read before send) can **slow down** or **replan**. See **Strong integration story** in [`../MASTER_PLAN.md`](../MASTER_PLAN.md).

## Your mission

- `POST /webhooks/twilio` (or similar) — parse Twilio form body (`From`, `Body`, etc.).
- Map phone number → `user_id` (stub table in Mongo later).
- Commands (MVP): `start`, `stuck`, `done` — translate to `POST /plan`, `POST /nudge`, `POST /session/*` as appropriate.
- **Outbound**: Twilio REST to send WhatsApp replies; reuse the same message templates T4 uses for Fetch-triggered pings.

**Stretch (optional):** The backend may route **free-form** WhatsApp text into the same **chat** pipeline as the web app (plus **`BUILD` / `yes` / `go`**-style finalize triggers). **If that path stays rough or unused, no problem** — MVP is still keyword commands + TwiML replies.

## Where to work

- `backend/app/routers/webhooks_twilio.py` — stub is present; implement Twilio validation (request signature) before hackathon demo.
- Coordinate with **T2** for any new DTOs.
- Coordinate with **T4** so Fetch-triggered sends and user replies use one Twilio helper (`backend/app/services/` — add as needed).

## Environment

- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM` in `backend/.env.example` (fill locally).

## Testing

- **Unit**: parse command strings from sample message bodies.
- **Integration**: use Twilio **test credentials** / sandbox; send one inbound webhook with `curl` or Twilio console.
- **Manual**: phone → sandbox → see reply.

## Checklist

- [ ] Inbound webhook returns TwiML or JSON as Twilio expects.
- [ ] No secrets in repo; use `.env` only.

See root [`README.md`](../../README.md).
