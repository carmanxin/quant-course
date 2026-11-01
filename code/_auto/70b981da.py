# @quantlab/output: 70b981da
def estimate_backtest_to_live_gap(backtest_sharpe: float,
                                   fill_rate_backtest: float,
                                   estimated_live_fill_rate: float,
                                   latency_ms: float,
                                   competition_index: float) -> dict:
    """
    估计从回测到实盘的性能衰减。

    参数:
        backtest_sharpe: 回测夏普比率
        fill_rate_backtest: 回测中的成交率
        estimated_live_fill_rate: 估计的实盘成交率
        latency_ms: 策略延迟（毫秒）
        competition_index: 竞争指数 [0, 1]，1表示极度竞争
    返回:
        包含性能衰减估计的字典
    """
    # 成交率衰减
    fill_decay = estimated_live_fill_rate / fill_rate_backtest

    # 滑点估计（基于延迟和竞争）
    slippage_bps = latency_ms * 0.1 * (1 + competition_index * 5)

    # 夏普衰减估计
    live_sharpe_estimate = backtest_sharpe * fill_decay * 0.7

    return {
        'fill_rate_decay': 1 - fill_decay,
        'estimated_slippage_bps': slippage_bps,
        'backtest_sharpe': backtest_sharpe,
        'estimated_live_sharpe': live_sharpe_estimate,
        'performance_decay_pct': (1 - live_sharpe_estimate / backtest_sharpe) * 100
    }
