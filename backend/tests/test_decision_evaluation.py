import json
from pathlib import Path

from app.decision_engine import evaluate_e204


def test_decision_cases_are_consistent():
    cases = json.loads((Path(__file__).parents[2] / "data" / "decision_evaluation_cases.json").read_text(encoding="utf-8"))
    for case in cases:
        result = evaluate_e204(case["input"])
        assert result["status"] == case["expected_status"]
        assert result["risk"] == case["expected_risk"]
