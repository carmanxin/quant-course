# @quantlab/output: 5ec7be22
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
