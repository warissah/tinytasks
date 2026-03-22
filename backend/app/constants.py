"""
Shared constants for API copy and Mongo collection names.

Mongo (MVP): persist coach output in **plans** only — not a separate **tasks** collection.
API fields named **task_id** (sessions, nudge, internal reminders) mean **plan_id** until T1
renames request bodies. See docs/plans/T2_BACKEND.md and docs/MASTER_PLAN.md.
"""

PLAN_SAFETY_NOTE = (
    "Non-clinical tool. If you are in crisis, contact local emergency services or 988 (US)."
)

# Motor / PyMongo collection names — use these symbols in repositories (avoid ad-hoc "tasks").
PLANS_COLLECTION = "plans"
SESSIONS_COLLECTION = "sessions"
CHAT_THREADS_COLLECTION = "chat_threads"
