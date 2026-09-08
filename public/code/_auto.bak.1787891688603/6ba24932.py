# @quantlab/output: 6ba24932
def rolling_var_backtest(returns, window=252, confidence=0.95):
    """
    滚动计算VaR并与实际损失对比，做VaR有效性检验

    理想情况下：实际损失超过VaR的比例应该接近 (1-confidence)
    如：95% VaR下，平均每20个交易日有1次被突破
    """
    roll_var = returns.rolling(window).apply(
        lambda x: -np.percentile(x, (1 - confidence) * 100)
    )

    # 实际损失（负收益的绝对值）
    losses = -returns

    # VaR突破：损失 > VaR（注意VaR通常为正数表示损失）
    breaches = (losses > roll_var.shift(1)).dropna()
    breach_rate = breaches.mean()

    # Kupiec检验的统计量
    n = len(breaches)
    n_breaches = breaches.sum()
    expected_rate = 1 - confidence

    # 似然比检验
    if n_breaches > 0 and n_breaches < n:
        LR = -2 * np.log(
            ((1 - expected_rate) ** (n - n_breaches) * expected_rate ** n_breaches) /
            ((1 - n_breaches/n) ** (n - n_breaches) * (n_breaches/n) ** n_breaches)
        )
        p_value = 1 - stats.chi2.cdf(LR, df=1)
    else:
        p_value = np.nan

    print(f"VaR突破率: {breach_rate:.2%} (期望: {expected_rate:.2%})")
    print(f"VaR突破次数: {n_breaches}/{n}")
    print(f"Kupiec检验p值: {p_value:.4f}")
    if p_value < 0.05:
        print("⚠️ VaR模型不准确（在5%水平下拒绝原假设）")
    else:
        print("✅ VaR模型通过回测检验")

    return roll_var, breaches
