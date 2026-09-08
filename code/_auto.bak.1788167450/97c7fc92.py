# @quantlab/output: 97c7fc92
def var_backtest_validation(var_forecasts: np.ndarray,
                             actual_returns: np.ndarray,
                             confidence_level: float = 0.99) -> dict:
    """
    全面的 VaR 回测验证。

    包括：Kupiec POF 检验、Christoffersen 独立性检验、
          Christoffersen 条件覆盖检验。

    参数:
        var_forecasts: VaR 预测值序列（应为正值表示损失）
        actual_returns: 实际收益率（以损失为正，即 -returns）
        confidence_level: VaR 置信水平
    返回:
        检验统计量和 p 值
    """
    T = len(actual_returns)

    # 例外指示灯 I_t = 1 if Loss > VaR else 0
    exceptions = (actual_returns > var_forecasts).astype(int)
    N = exceptions.sum()
    alpha = 1 - confidence_level

    # 1. Kupiec POF 检验
    p_hat = N / T
    if p_hat == 0:
        lr_pof = -2 * (T * np.log(1 - alpha))
    elif p_hat == 1:
        lr_pof = -2 * (T * np.log(alpha))
    else:
        lr_pof = -2 * (np.log((1 - alpha)**(T - N) * alpha**N) -
                       np.log((1 - p_hat)**(T - N) * p_hat**N))

    p_value_pof = 1 - stats.chi2.cdf(lr_pof, 1)

    # 2. Christoffersen 独立性检验
    n00 = np.sum((exceptions[:-1] == 0) & (exceptions[1:] == 0))
    n01 = np.sum((exceptions[:-1] == 0) & (exceptions[1:] == 1))
    n10 = np.sum((exceptions[:-1] == 1) & (exceptions[1:] == 0))
    n11 = np.sum((exceptions[:-1] == 1) & (exceptions[1:] == 1))

    # 转移概率
    p01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0
    p11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0
    p = (n01 + n11) / (n00 + n01 + n10 + n11)

    if p01 == 0 or p11 == 0 or p == 0:
        lr_ind = 0
    else:
        lr_ind = -2 * (np.log((1 - p)**(n00 + n10) * p**(n01 + n11)) -
                       np.log((1 - p01)**n00 * p01**n01 *
                              (1 - p11)**n10 * p11**n11))

    p_value_ind = 1 - stats.chi2.cdf(lr_ind, 1)

    # 3. 条件覆盖检验 (Conditional Coverage)
    lr_cc = lr_pof + lr_ind
    p_value_cc = 1 - stats.chi2.cdf(lr_cc, 2)

    return {
        'T': T, 'N_exceptions': N, 'exception_rate': N / T,
        'expected_rate': alpha,
        'Kupiec_POF_LR': lr_pof, 'Kupiec_POF_pvalue': p_value_pof,
        'Christoffersen_Ind_LR': lr_ind,
        'Christoffersen_Ind_pvalue': p_value_ind,
        'Christoffersen_CC_LR': lr_cc,
        'Christoffersen_CC_pvalue': p_value_cc,
        'model_valid': p_value_cc > 0.05  # 5%显著性水平
    }
