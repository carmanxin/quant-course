# @quantlab/output: 3b4ef0ed
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

def estimate_factor_exposure(returns, factors, risk_free=0.0):
    """
    估计资产或策略对FF三因子的暴露，提取Alpha

    returns: 资产/策略的日收益率序列（超额收益，已减去无风险利率）
    factors: DataFrame, 至少包含 MKT, SMB, HML 三列
    """
    # 对齐数据
    data = pd.concat([returns, factors], axis=1).dropna()
    y = data.iloc[:, 0]  # 第一列为收益率
    X = data.iloc[:, 1:]  # 其余为因子

    # 添加常数项（Alpha）
    X = sm.add_constant(X)

    # OLS回归
    model = sm.OLS(y, X).fit()

    # 提取结果
    alpha = model.params['const']
    alpha_t = model.tvalues['const']
    alpha_p = model.pvalues['const']

    print("=== 因子暴露分析 ===")
    print(f"Alpha (年化): {alpha * 252:.2%}")
    print(f"Alpha t值: {alpha_t:.3f}")
    print(f"Alpha p值: {alpha_p:.4f}")
    print(f"R-squared: {model.rsquared:.4f}")
    print(f"\n因子暴露:")
    for factor_name in factors.columns:
        coef = model.params[factor_name]
        pval = model.pvalues[factor_name]
        significance = '***' if pval < 0.001 else ('**' if pval < 0.01 else ('*' if pval < 0.05 else ''))
        print(f"  {factor_name}: {coef:.4f} {significance} (p={pval:.4f})")

    return model

def rolling_factor_analysis(returns, factors, window=252):
    """
    滚动窗口分析因子暴露的时变性
    """
    n = len(returns)
    rolling_alpha = np.full(n, np.nan)
    rolling_alpha_t = np.full(n, np.nan)

    for t in range(window, n):
        ret_window = returns.iloc[t-window:t]
        fac_window = factors.iloc[t-window:t]

        data = pd.concat([ret_window, fac_window], axis=1).dropna()
        if len(data) < window * 0.8:
            continue

        y = data.iloc[:, 0]
        X = sm.add_constant(data.iloc[:, 1:])

        try:
            model = sm.OLS(y, X).fit()
            rolling_alpha[t] = model.params['const'] * 252  # 年化
            rolling_alpha_t[t] = model.tvalues['const']
        except:
            continue

    return rolling_alpha, rolling_alpha_t

# 使用示例
# factors_df = pd.DataFrame({
#     'Mkt-RF': market_returns - risk_free,
#     'SMB': smb_series,
#     'HML': hml_series
# })
# strategy_excess = strategy_returns - risk_free_rate
# model = estimate_factor_exposure(strategy_excess, factors_df)
