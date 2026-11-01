# @quantlab/output: 8428c730
def vix_spx_convexity_profile(spx_changes: np.ndarray,
                               vix_changes: np.ndarray) -> dict:
    """
    量化 VIX 对 SPX 变动的凸性响应（不对称性）。

    VIX 对下跌的敏感度远大于对上涨的敏感度。
    """
    # 分别拟合下跌和上涨时的回归
    down_mask = spx_changes < 0
    up_mask = spx_changes >= 0

    # 下跌时的敏感度（应更大、更负）
    beta_down = np.polyfit(spx_changes[down_mask],
                            vix_changes[down_mask], 1)[0]

    # 上涨时的敏感度
    beta_up = np.polyfit(spx_changes[up_mask],
                          vix_changes[up_mask], 1)[0]

    # 凸性比率
    convexity_ratio = abs(beta_down / beta_up) if beta_up != 0 else np.inf

    return {
        'beta_downside': beta_down,
        'beta_upside': beta_up,
        'convexity_ratio': convexity_ratio,
        'asymmetric': convexity_ratio > 2.0,
        'tail_hedge_effectiveness': (
            'High' if convexity_ratio > 3.0 else
            'Medium' if convexity_ratio > 2.0 else
            'Low'
        )
    }
