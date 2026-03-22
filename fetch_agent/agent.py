import os
import requests
from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

load_dotenv()



BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "replace-with-long-random-string")

# Hardcoded for demo — swap with real user/task IDs from Mongo when ready
DEMO_USER_ID = "demo-user-001"
DEMO_TASK_ID = "demo-task-001"

agent = Agent(
    name="adhd_reminder_agent",
    seed=os.getenv("AGENT_SEED", "adhd-coach-reminder-seed-phrase"),
    port=8001,
    mailbox=True,
    publish_agent_details=True,
)


@agent.on_interval(period=900.0)  # every 15 minutes
async def fire_reminder(ctx: Context):
    payload = {
        "user_id": DEMO_USER_ID,
        "task_id": DEMO_TASK_ID,
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
