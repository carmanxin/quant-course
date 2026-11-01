# @quantlab/output: c7a3f120
from scipy import stats

def strategy_significance_test(returns, rf_rate=0.03):
    """
    多种统计检验全面评估策略的显著性
    """
    results = {}

    # 1. 单样本t检验：H0: mean(returns) = 0
    t_stat, p_value = stats.ttest_1samp(returns, 0)
    results['t-test_pvalue'] = p_value
    results['t-test_significant'] = p_value < 0.05

    # 2. 方差比率检验：检验收益率是否为随机游走
    # Var(r_{t,t+k}) / (k * Var(r_t)) 应在1附近
    k = 5
    k_period_returns = returns.rolling(k).sum().dropna()
    var_ratio = k_period_returns.var() / (k * returns.var())
    results['variance_ratio'] = var_ratio

    # 3. 符号检验：正收益天数是否显著多于50%
    n_pos = (returns > 0).sum()
    n_total = len(returns)
    sign_p_value = stats.binomtest(n_pos, n_total, p=0.5, alternative='greater').pvalue
    results['sign_test_pvalue'] = sign_p_value

    # 4. 自相关检验：Ljung-Box检验收益率是否存在显著自相关
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb_result = acorr_ljungbox(returns, lags=[10], return_df=True)
    results['ljung_box_pvalue'] = lb_result['lb_pvalue'].values[0]
    results['has_autocorr'] = results['ljung_box_pvalue'] < 0.05

    # 5. Bootstrap夏普的置信区间
    boot_sharpes = []
    for _ in range(1000):
        bt = np.random.choice(returns, size=len(returns), replace=True)
        boot_sharpes.append(bt.mean() / bt.std() * np.sqrt(252))
    results['sharpe_95ci'] = (np.percentile(boot_sharpes, 2.5),
                               np.percentile(boot_sharpes, 97.5))

    return pd.Series(results)
