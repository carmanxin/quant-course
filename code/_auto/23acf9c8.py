# @quantlab/output: 23acf9c8
def optimal_leverage(strategy_sharpe, annual_vol, max_leverage=5.0, safety_factor=0.5):
    """
    基于夏普比和波动率的最优杠杆计算
    safety_factor: 0.5 = 半凯利准则
    """
    # Kelly 最优杠杆
    excess_return = strategy_sharpe * annual_vol  # 超额收益
    kelly_leverage = excess_return / (annual_vol ** 2)

    # 应用安全系数并设置上限
    recommended_leverage = min(kelly_leverage * safety_factor, max_leverage)

    return {
        'kelly_leverage': kelly_leverage,
        'recommended_leverage': recommended_leverage,
        'max_drawdown_estimate': 1 - np.exp(-2 * recommended_leverage)  # 简化的回撤估计
    }
