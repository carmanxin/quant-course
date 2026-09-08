# @quantlab/output: 444e230d
import pandas as pd
import numpy as np
from scipy.stats import norm

class ETFOptionsBacktest:
    """50ETF 期权策略回测框架"""
    def __init__(self, prices, r=0.025):
        self.prices = prices  # pd.Series of 50ETF close
        self.r = r

    def bs(self, S, K, T, sigma, otype="call"):
        if T <= 0: return max(S-K, 0) if otype=="call" else max(K-S, 0)
        d1 = (np.log(S/K) + (self.r+sigma**2/2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        return S*norm.cdf(d1)-K*np.exp(-self.r*T)*norm.cdf(d2) if otype=="call" \
            else K*np.exp(-self.r*T)*norm.cdf(-d2)-S*norm.cdf(-d1)

    def covered_call(self, otm_pct=0.05, hold_days=30):
        """备兑开仓:每日持有 ETF + 卖 OTM Call"""
        results = []
        for i in range(0, len(self.prices) - hold_days, hold_days):
            S = self.prices.iloc[i]
            sigma = self.realized_vol(i, 20)
            K_short = round((1 + otm_pct) * S / 0.025) * 0.025  # 行权价取整
            T = hold_days / 365
            premium = self.bs(S, K_short, T, sigma, "call")
            S_T = self.prices.iloc[i + hold_days]
            # 损益 = ETF 涨跌 + Call 损益
            etf_pnl = (S_T - S) * 10000
            call_pnl = premium * 10000 - max(S_T - K_short, 0) * 10000
            results.append(etf_pnl + call_pnl)
        return pd.Series(results)

    def realized_vol(self, idx, window=20):
        """基于历史 20 天波动率"""
        if idx < window:
            window = idx
        rets = np.log(self.prices.iloc[idx-window:idx+1]).diff().dropna()
        return rets.std() * np.sqrt(252)

# 使用示例
# prices = ak.fund_etf_hist_em("510050").close  # 50ETF 日线
# bt = ETFOptionsBacktest(prices)
# cc_pnl = bt.covered_call()
