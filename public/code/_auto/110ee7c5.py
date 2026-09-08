# @quantlab/output: 110ee7c5
def audit_star(answer: dict[str, str]) -> list[str]:
    required = {"situation", "task", "action", "result"}
    missing = sorted(required - answer.keys())
    issues = [f"缺少字段：{name}" for name in missing]
    if "result" in answer and not any(ch.isdigit() for ch in answer["result"]):
        issues.append("结果缺少量化证据")
    if "action" in answer and len(answer["action"]) < 40:
        issues.append("行动过于概括，需要说明个人决策与取舍")
    return issues


sample = {
    "situation": "回测夏普异常升至 3.1。",
    "task": "定位收益虚高原因。",
    "action": "逐字段核对可得时间，并重建带公告时间戳的 Point-in-Time 数据集。",
    "result": "修复后夏普为 1.4，并拦截后续 2 次同类泄漏。",
}
print(audit_star(sample) or "STAR 证据链完整")
