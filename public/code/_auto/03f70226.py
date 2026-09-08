# @quantlab/output: 03f70226
def strategy_capital_efficiency(annualized_return: float,
                                 annualized_volatility: float,
                                 rwa_charge: float,
                                 capital_ratio: float = 0.08,
                                 hurdle_rate: float = 0.15) -> dict:
    """
    计算策略的资本效率和风险调整后收益。

    参数:
        annualized_return: 策略年化预期收益（元）
        annualized_volatility: 年化波动率（元）
        rwa_charge: 策略的风险加权资产占用（元）
        capital_ratio: 最低资本充足率
        hurdle_rate: 股权资本的最低要求回报率
    返回:
        资本效率指标
    """
    # 所需监管资本
    required_capital = rwa_charge * capital_ratio

    # 资本回报率
    roc = annualized_return / required_capital * 100

    # 风险调整后资本回报率
    raroc = annualized_return / (required_capital * 2) * 100

    # 经济利润（扣除资本成本）
    economic_profit = annualized_return - required_capital * hurdle_rate

    # 夏普比率
    sharpe = annualized_return / annualized_volatility

    return {
        'Required_Capital': required_capital,
        'ROC': roc,
        'RAROC': raroc,
        'Economic_Profit': economic_profit,
        'Sharpe_Ratio': sharpe,
        'Capital_Efficient': roc > hurdle_rate * 100
    }
