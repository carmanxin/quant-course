# @quantlab/output: 0571e250
def fed_balance_sheet_impact(fed_assets_change_pct: float,
                              equity_returns: np.ndarray,
                              bond_yield_change: np.ndarray,
                              window: int = 60) -> dict:
    """
    量化美联储资产负债表变化对资产价格的影响。

    参数:
        fed_assets_change_pct: 美联储总资产的月度变化率
        equity_returns: 同期权益市场收益率
        bond_yield_change: 同期国债收益率变动
        window: 滚动窗口大小
    返回:
        影响分析结果
    """
    # 相关性分析
    eq_corr = np.corrcoef(fed_assets_change_pct[-window:],
                           equity_returns[-window:])[0, 1]
    bond_corr = np.corrcoef(fed_assets_change_pct[-window:],
                              bond_yield_change[-window:])[0, 1]

    # 回归：权益收益 = α + β * ΔFedAssets + ε
    X = np.column_stack([np.ones(len(fed_assets_change_pct)),
                          fed_assets_change_pct])
    y = equity_returns

    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    eq_beta = beta[1]

    # 回归：债券收益变动 = α + β * ΔFedAssets + ε
    beta_bond = np.linalg.lstsq(
        X, bond_yield_change, rcond=None
    )[0]
    bond_beta = beta_bond[1]

    return {
        'equity_correlation': eq_corr,
        'bond_yield_correlation': bond_corr,
        'equity_beta_to_fed_bs': eq_beta,
        'bond_beta_to_fed_bs': bond_beta,
        'interpretation': (
            'QE推升权益、压低债券收益率' if eq_beta > 0 and bond_beta < 0
            else '关联不显著或方向异常'
        )
    }
