# @quantlab/output: d3b2d3a7
def reallocate_capital(retired_strategy_capital: float,
                       active_strategies: dict,
                       new_strategies: list) -> dict:
    """
    策略退役后资金再配置

    Parameters
    ----------
    retired_strategy_capital : float
        退役策略释放的资金
    active_strategies : dict
        现有活跃策略，{strategy_id: {capital, vol, sharpe}}
    new_strategies : list
        待引入的新策略列表
    """
    # 1. 计算现有策略的风险贡献
    total_risk = sum(s['vol'] * s['capital'] for s in active_strategies.values())

    # 2. 按对等风险贡献原则分配
    target_risk_contribution = (total_risk + retired_strategy_capital * 0.15) / \
                                (len(active_strategies) + max(len(new_strategies), 1))

    allocations = {}

    # 现有策略的增量分配
    for sid, strat in active_strategies.items():
        current_risk_contrib = strat['vol'] * strat['capital']
        if current_risk_contrib > 0:
            # 缩放到目标风险贡献
            target_capital = target_risk_contribution / strat['vol']
            delta = target_capital - strat['capital']
            allocations[sid] = {
                'current': strat['capital'],
                'target': target_capital,
                'delta': delta,
                'action': 'INCREASE' if delta > 0 else 'DECREASE'
            }

    # 新策略的初始分配（如果有）
    remaining = retired_strategy_capital - sum(a['delta'] for a in allocations.values())
    if new_strategies and remaining > 0:
        per_new = remaining / len(new_strategies)
        for ns in new_strategies:
            allocations[ns['id']] = {
                'current': 0,
                'target': per_new,
                'delta': per_new,
                'action': 'NEW_ALLOCATION'
            }

    return allocations
