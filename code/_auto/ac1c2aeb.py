# @quantlab/output: ac1c2aeb
def cash_and_carry_analysis(spot_price, perp_price, funding_rate_annualized,
                             holding_days, transaction_cost_bps=10):
    """
    永续合约期现套利分析
    """
    # 价差（年化百分比）
    premium = (perp_price - spot_price) / spot_price

    # 预期年度化收益
    # 收益 = 价差收敛 + 资金费率收入 - 交易成本
    entry_cost = transaction_cost_bps / 10000 * 2  # 买卖各一次
    annualized_return = premium + funding_rate_annualized - entry_cost * (365 / holding_days)

    # 如果持有期间价差完全收敛
    holding_period_return = annualized_return * holding_days / 365

    return {
        'spot_price': spot_price,
        'perp_price': perp_price,
        'premium_bps': premium * 10000,
        'funding_rate_annualized_pct': funding_rate_annualized * 100,
        'holding_period_return_pct': holding_period_return * 100,
        'annualized_return_pct': annualized_return * 100,
        'feasible': holding_period_return > 0
    }

# 示例
print(cash_and_carry_analysis(
    spot_price=50000, perp_price=50050,
    funding_rate_annualized=0.12,  # 12%年化资金费率
    holding_days=30
))
