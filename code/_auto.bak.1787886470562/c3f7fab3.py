# @quantlab/output: c3f7fab3
import numpy as np
import pandas as pd

def calculate_funding_rate(premium_index, cap=0.00375, interval_hours=8):
    """
    计算永续合约资金费率
    premium_index: 标记价相对于指数价的溢价
    cap: 资金费率上限（通常 0.375% per 8h）
    interval_hours: 资金费率结算间隔
    """
    # 基础费率 = 溢价 / 时间间隔
    base_rate = premium_index / interval_hours

    # Clamp 到 [-cap, +cap]
    funding_rate = np.clip(base_rate, -cap, cap)

    # 资金费用 = 持仓名义价值 * 资金费率
    # funding_payment = position_value * funding_rate

    return funding_rate


def simulate_funding_payments(position_value, funding_rates):
    """
    模拟一段时间的资金费率支出/收入
    positive position_value = 多头
    negative position_value = 空头
    """
    payments = []
    cumulative = 0

    for rate in funding_rates:
        payment = -position_value * rate  # 多头支付 (负值=支出)
        cumulative += payment
        payments.append({
            'funding_rate': rate,
            'payment': payment,
            'cumulative': cumulative
        })

    return pd.DataFrame(payments)

# 示例：做多1 BTC，在极高资金费率环境下的成本
btc_price = 50000
high_funding_scenario = [0.00375] * 3  # 3个8小时周期，封顶费率
payments = simulate_funding_payments(btc_price, high_funding_scenario)
print(f"3个周期（24小时）的资金费率支出: ${payments['payment'].sum():.0f}")
print(f"年化资金费率成本: {payments['funding_rate'].mean() * 3 * 365 * 100:.2f}%")
