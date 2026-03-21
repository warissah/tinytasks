# T3 — WhatsApp (Twilio)

You own **inbound** webhooks and **outbound** messages. Business logic stays in **T2’s** services — you **call the same endpoints** the web app uses (or thin wrappers), so behavior stays consistent.

## Your mission

- `POST /webhooks/twilio` (or similar) — parse Twilio form body (`From`, `Body`, etc.).
- Map phone number → `user_id` (stub table in Mongo later).
- Commands (MVP): `start`, `stuck`, `done` — translate to `POST /plan`, `POST /nudge`, `POST /session/*` as appropriate.
- **Outbound**: Twilio REST to send WhatsApp replies; reuse the same message templates T4 uses for Fetch-triggered pings.

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
