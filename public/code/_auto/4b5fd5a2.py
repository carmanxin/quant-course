# @quantlab/output: 4b5fd5a2
import numpy as np
import pandas as pd
from typing import Tuple

def fx_carry_strategy(spot_rates: pd.DataFrame,
                       interest_rates: pd.DataFrame,
                       lookback_days: int = 21) -> pd.DataFrame:
    """
    系统性外汇套息策略。

    每月做多利率最高的3种货币，做空利率最低的3种货币。

    参数:
        spot_rates: 外汇即期汇率（每列为一种货币对）
        interest_rates: 对应货币的短期利率（年化%）
        lookback_days: 调仓周期
    返回:
        策略收益率序列
    """
    n_currencies = len(interest_rates.columns)

    returns = spot_rates.pct_change().fillna(0)
    strategy_returns = []

    for t in range(lookback_days, len(interest_rates), lookback_days):
        # 当前利率排名
        current_rates = interest_rates.iloc[t]
        ranked = current_rates.sort_values()

        # 高利率货币做多，低利率货币做空
        long_currencies = ranked.index[-3:]  # 最高利率的3种
        short_currencies = ranked.index[:3]   # 最低利率的3种

        # 下一持仓期的收益
        end_idx = min(t + lookback_days, len(returns))
        period_returns = returns.iloc[t:end_idx]

        # 组合收益（等权多空）
        long_return = period_returns[long_currencies].mean(axis=1)
        short_return = period_returns[short_currencies].mean(axis=1)
        portfolio_return = long_return - short_return

        strategy_returns.append(portfolio_return)

    # 拼接
    strategy_returns = pd.concat(strategy_returns)
    strategy_returns = strategy_returns[~strategy_returns.index.duplicated()]

    return strategy_returns

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(17)
_ccys = ['EUR', 'JPY', 'GBP', 'AUD']
_idx = pd.date_range('2023-01-02', periods=250)
_spot = pd.DataFrame({c: [1.1, 150, 1.27, 0.67][i] + np.cumsum(np.random.randn(250) * 0.004)
                      for i, c in enumerate(_ccys)}, index=_idx)
_rates = pd.DataFrame({c: [3.5, 0.1, 4.8, 4.2][i] + np.random.randn(250) * 0.02
                       for i, c in enumerate(_ccys)}, index=_idx)
_carry = fx_carry_strategy(_spot, _rates)
print('套息策略累计收益:', round(float((1 + _carry.fillna(0)).prod() - 1), 4))
