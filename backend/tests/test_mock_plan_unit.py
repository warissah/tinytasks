from app.services.mock_plan import build_stub_plan


def test_build_stub_plan_has_stable_fields() -> None:
    plan = build_stub_plan("Write essay")
    assert plan.plan_id
    assert plan.tiny_first_step.estimated_minutes >= 1
    assert len(plan.steps) >= 1
