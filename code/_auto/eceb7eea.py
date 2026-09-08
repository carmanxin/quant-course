# @quantlab/output: eceb7eea
from __future__ import annotations

import re


WEAK_WORDS = {"参与", "负责相关", "取得较好", "熟悉", "了解"}
EVIDENCE_WORDS = {"样本外", "成本", "基准", "延迟", "吞吐", "容量", "置信区间"}


def audit_bullet(text: str) -> dict[str, object]:
    numbers = re.findall(r"\d+(?:\.\d+)?%?|\d+(?:\.\d+)?\s*(?:ms|us|bps)", text)
    weak = sorted(word for word in WEAK_WORDS if word in text)
    evidence = sorted(word for word in EVIDENCE_WORDS if word in text)
    return {
        "length": len(text),
        "numbers": numbers,
        "weak_words": weak,
        "evidence_terms": evidence,
        "pass": 55 <= len(text) <= 180 and bool(numbers) and not weak and len(evidence) >= 2,
    }


bullet = "使用机器学习开发选股策略，取得较好收益。"
print(audit_bullet(bullet))

better = (
    "基于 Point-in-Time A 股数据构建质量因子；在锁定样本外 Rank IC 0.031，"
    "扣除双边 20 bps 成本后 Sharpe 1.24，并完成容量压力测试。"
)
print(audit_bullet(better))
