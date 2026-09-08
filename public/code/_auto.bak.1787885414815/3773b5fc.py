# @quantlab/output: 3773b5fc
def taylor_rule_ffr(inflation: float,
                     inflation_target: float,
                     output_gap: float,
                     r_star: float = 2.0) -> float:
    """
    原始泰勒规则计算建议的联邦基金利率。

    参数:
        inflation: 当前通胀率（%）
        inflation_target: 通胀目标（%，通常为2）
        output_gap: 产出缺口（%）
        r_star: 自然真实利率（%）
    返回:
        泰勒规则建议的FFR（%）
    """
    ffr_recommended = r_star + inflation + \
        0.5 * (inflation - inflation_target) + \
        0.5 * output_gap

    return max(0, ffr_recommended)


def taylor_rule_residual(actual_ffr: float,
                          inflation: float,
                          inflation_target: float,
                          output_gap: float,
                          r_star: float = 2.0) -> float:
    """
    泰勒规则残差 = 实际FFR - 泰勒规则建议FFR。

    正值表示政策偏紧，负值表示政策偏松。
    """
    recommended = taylor_rule_ffr(inflation, inflation_target,
                                   output_gap, r_star)
    residual = actual_ffr - recommended
    return residual
