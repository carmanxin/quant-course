# @quantlab/output: 5aeb603f
def diffusion_index(indicator_changes: np.ndarray) -> float:
    """
    计算领先指标的扩散指数。

    扩散指数 = (上升的指标数 / 总指标数) × 100
    当DI > 50时，多数指标扩张；DI < 50时，多数收缩。

    参数:
        indicator_changes: 各指标的最新变化（正=扩张，负=收缩）
    返回:
        扩散指数 [0, 100]
    """
    n_up = np.sum(indicator_changes > 0)
    n_total = len(indicator_changes)

    di = (n_up / n_total) * 100

    return di
