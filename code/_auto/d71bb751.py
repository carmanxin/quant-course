# @quantlab/output: d71bb751
import numpy as np

def risk_budget_dashboard(current_rc_pct: np.ndarray,
                           target_budgets: np.ndarray,
                           labels: list) -> dict:
    """
    风险预算监控仪表板：比较实际 vs 目标风险贡献。

    返回:
        包含偏差分析和预警信号的字典
    """
    deviations = current_rc_pct - target_budgets * 100
    abs_deviations = np.abs(deviations)

    # 预警：偏差超过阈值
    threshold = 5  # 5个百分点
    alerts = []
    for i, dev in enumerate(deviations):
        if abs(dev) > threshold:
            direction = 'over' if dev > 0 else 'under'
            alerts.append(f"{labels[i]}: {direction}-allocated "
                          f"({dev:+.1f}pp vs budget)")

    return {
        'current_contribution': dict(zip(labels, current_rc_pct)),
        'target_budget': dict(zip(labels, target_budgets * 100)),
        'deviations': dict(zip(labels, deviations)),
        'max_deviation': np.max(abs_deviations),
        'alerts': alerts,
        'rebalance_needed': len(alerts) > 0
    }

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_rc = np.array([38, 22, 27, 13])
_tb = np.array([0.4, 0.3, 0.2, 0.1])
_db = risk_budget_dashboard(_rc, _tb, labels=['股票', '债券', '商品', '现金'])
for _k, _v in _db.items():
    print(f'{_k}: {_v}')
