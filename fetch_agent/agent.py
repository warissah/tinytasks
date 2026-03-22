import os
import requests
from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "https://tinytasks.up.railway.app").rstrip("/")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "replace-with-long-random-string")

DEMO_USER_ID = os.getenv("DEMO_USER_ID", "demo-user-001")
# Leave DEMO_TASK_ID empty to auto-resolve the latest plan from the backend
_task_id_cache = os.getenv("DEMO_TASK_ID", "")

agent = Agent(
    name="adhd_reminder_agent",
    seed=os.getenv("AGENT_SEED", "adhd-coach-reminder-seed-phrase"),
    port=8001,
    mailbox=True,
    publish_agent_details=True,
)


def _resolve_task_id(ctx: Context) -> str:
    global _task_id_cache
    if _task_id_cache:
        return _task_id_cache
    try:
        resp = requests.get(
            f"{BACKEND_URL}/internal/latest-plan",
            headers={"X-Internal-Key": INTERNAL_API_KEY},
            timeout=5,
        )
        if resp.ok:
            plan_id = resp.json().get("plan_id", "")
            if plan_id:
                ctx.logger.info(f"Resolved latest plan_id={plan_id}")
                _task_id_cache = plan_id
                return plan_id
    except Exception as e:
        ctx.logger.warning(f"Could not fetch latest plan_id: {e}")
    return "demo-task-001"


@agent.on_interval(period=900.0)  # every 15 minutes
async def fire_reminder(ctx: Context):
    task_id = _resolve_task_id(ctx)

    payload = {
        "user_id": DEMO_USER_ID,
        "task_id": task_id,
        "reminder_kind": "check_in_15m",
        "agent_context": {
            "energy_hint": "unknown",
            "push_back_start_minutes": 0,
            "replan_intensity": "same",
        },
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/internal/reminders/fire",
            json=payload,
            headers={"X-Internal-Key": INTERNAL_API_KEY},
            timeout=10,
        )
        ctx.logger.info(f"Fired reminder: {response.status_code} {response.text}")
    except Exception as e:
        ctx.logger.error(f"Failed to fire reminder: {e}")


if __name__ == "__main__":
    agent.run()
