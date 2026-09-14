from app.decision_engine import evaluate_e204


def test_e204_requires_safety_conditions():
    result = evaluate_e204({"power_off": None, "connector_condition": None})
    assert result["status"] == "NEEDS_INPUT"
    assert "不得直接复位后继续运行" in result["prohibited_actions"]


def test_e204_blocks_overheating():
    result = evaluate_e204({"power_off": True, "connector_condition": "正常", "overheating": True})
    assert result["status"] == "BLOCKED"
    assert result["risk"] == "CRITICAL"


def test_e204_recommends_sensor_path_for_repeated_alarm():
    result = evaluate_e204({"power_off": True, "connector_condition": "腐蚀", "recent_count": 4, "operating_hours": 8600})
    assert result["status"] == "READY"
    assert result["risk"] == "HIGH"
    assert any("连接器" in action for action in result["actions"])
