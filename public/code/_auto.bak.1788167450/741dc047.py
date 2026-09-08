# @quantlab/output: 741dc047
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt

def otm_put_tail_hedge(portfolio_value: float,
                        protection_level: float = 0.80,
                        spot_price: float = 100.0,
                        volatility: float = 0.20,
                        risk_free_rate: float = 0.03,
                        maturity_days: int = 90) -> dict:
    """
    设计基于 OTM 看跌期权的尾部对冲方案。

    参数:
        portfolio_value: 组合总价值
        protection_level: 保护水平（如0.80=保护20%的回撤）
        spot_price: 标的当前价格
        volatility: 隐含波动率
        risk_free_rate: 无风险利率
        maturity_days: 期权到期天数
    返回:
        对冲方案详情
    """
    T = maturity_days / 365

    # 目标保护价格
    strike_price = spot_price * protection_level

    # Black-Scholes 定价
    d1 = (np.log(spot_price / strike_price) +
          (risk_free_rate + volatility**2 / 2) * T) / \
         (volatility * np.sqrt(T))
    d2 = d1 - volatility * np.sqrt(T)

    put_price = strike_price * np.exp(-risk_free_rate * T) * \
                norm.cdf(-d2) - spot_price * norm.cdf(-d1)

    # 期权的 Delta (负值)
    put_delta = -norm.cdf(-d1)

    # 对冲比率：每保护 1 元组合价值需要多少期权
    protection_per_option = abs(put_delta) * spot_price
    n_options = portfolio_value / protection_per_option

    # 对冲成本
    total_premium = n_options * put_price
    premium_pct = total_premium / portfolio_value * 100

    # 年化对冲成本
    annualized_cost = premium_pct * (365 / maturity_days)

    # 在尾部事件中的回报（假设下跌40%）
    crash_scenario = spot_price * 0.60
    crash_put_value = max(strike_price - crash_scenario, 0)
    crash_hedge_gain = n_options * crash_put_value
    crash_portfolio_loss = portfolio_value * 0.40
    crash_net_impact = crash_hedge_gain - crash_portfolio_loss - total_premium

    return {
        'Strike_Price': strike_price,
        'Strike_Pct_of_Spot': protection_level * 100,
        'Put_Price': put_price,
        'Put_Delta': put_delta,
        'Number_of_Options': n_options,
        'Total_Premium': total_premium,
        'Premium_Pct': premium_pct,
        'Annualized_Cost_bps': annualized_cost * 100,
        'Crash_Scenario_Hedge_Gain': crash_hedge_gain,
        'Crash_Scenario_Net': crash_net_impact,
        'Crash_Scenario_Covered_Pct': (
            crash_hedge_gain / crash_portfolio_loss * 100
        )
    }
