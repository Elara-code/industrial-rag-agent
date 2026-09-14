from __future__ import annotations


def evaluate_e204(data: dict) -> dict:
    missing = [name for name in ("power_off", "connector_condition") if data.get(name) is None]
    overheating = data.get("overheating") is True
    if missing:
        return {"status": "NEEDS_INPUT", "risk": "HIGH", "conclusion": "无法确认下一步，必须补充现场条件。", "missing_conditions": missing, "actions": [], "prohibited_actions": ["不得直接复位后继续运行"], "escalation": "补充断电状态、连接器状态后再判断。", "sources": ["設備保守マニュアル.pdf:p3", "設備保守マニュアル.pdf:p4", "設備保守マニュアル.pdf:p5"]}
    if overheating or data.get("power_off") is False:
        return {"status": "BLOCKED", "risk": "CRITICAL", "conclusion": "立即停止操作并由负责人确认安全状态。", "missing_conditions": [], "actions": ["停止运行", "关闭主电源", "冷却后再进行点检"], "prohibited_actions": ["不得继续运行", "不得只做错误复位"], "escalation": "立即升级至维修主管；有过热风险时联系厂商。", "sources": ["設備保守マニュアル.pdf:p3", "設備保守マニュアル.pdf:p4"]}
    actions = ["检查冷却水温传感器", "检查连接器和配线"]
    if data.get("connector_condition") in {"锈蚀", "腐蚀", "损伤"}:
        actions.insert(0, "使用接点クリーナー清洁或更换连接器")
    if data.get("sensor_resistance") == "异常":
        actions.insert(0, "更换冷却水温传感器（SEN-TMP-003）")
    if (data.get("recent_count") or 0) >= 3 or (data.get("operating_hours") or 0) >= 8000:
        risk, conclusion = "HIGH", "E-204 有重复或高运行小时风险，建议安排计划点检，不建议仅复位后继续运行。"
        escalation = "点检后仍复发时升级检查控制基板 ECM。"
    else:
        risk, conclusion = "MEDIUM", "建议按保养手册完成传感器回路点检，并记录检查结果。"
        escalation = "无法确认原因或再次发生时升级至维修主管。"
    return {"status": "READY", "risk": risk, "conclusion": conclusion, "missing_conditions": [], "actions": actions, "prohibited_actions": ["不得只做错误复位后继续运行"], "escalation": escalation, "sources": ["設備保守マニュアル.pdf:p3", "設備保守マニュアル.pdf:p4", "設備保守マニュアル.pdf:p5"]}
