# @quantlab/output: a80f88be
def brinson_attribution(portfolio_weights: np.ndarray,
                         benchmark_weights: np.ndarray,
                         portfolio_sector_returns: np.ndarray,
                         benchmark_sector_returns: np.ndarray,
                         sector_names: list = None) -> pd.DataFrame:
    """
    Brinson 绩效归因模型。

    参数:
        portfolio_weights: (S,) 组合在各板块的权重
        benchmark_weights: (S,) 基准在各板块的权重
        portfolio_sector_returns: (S,) 组合在各板块的收益
        benchmark_sector_returns: (S,) 基准在各板块的收益
        sector_names: 板块名称列表
    返回:
        归因结果DataFrame
    """
    S = len(portfolio_weights)
    if sector_names is None:
        sector_names = [f'Sector {i+1}' for i in range(S)]

    # 基准总收益
    R_B = np.sum(benchmark_weights * benchmark_sector_returns)
    R_P = np.sum(portfolio_weights * portfolio_sector_returns)

    # 各效应
    allocation_effect = (portfolio_weights - benchmark_weights) * \
                        (benchmark_sector_returns - R_B)

    selection_effect = benchmark_weights * \
                       (portfolio_sector_returns - benchmark_sector_returns)

    interaction_effect = (portfolio_weights - benchmark_weights) * \
                         (portfolio_sector_returns - benchmark_sector_returns)

    results = pd.DataFrame({
        'Sector': sector_names,
        'Portfolio_Weight': portfolio_weights,
        'Benchmark_Weight': benchmark_weights,
        'Active_Weight': portfolio_weights - benchmark_weights,
        'Portfolio_Return': portfolio_sector_returns,
        'Benchmark_Return': benchmark_sector_returns,
        'Allocation_Effect': allocation_effect,
        'Selection_Effect': selection_effect,
        'Interaction_Effect': interaction_effect,
        'Total_Effect': allocation_effect + selection_effect + interaction_effect
    })

    # 加总行
    total_row = pd.DataFrame({
        'Sector': ['TOTAL'],
        'Portfolio_Weight': [np.sum(portfolio_weights)],
        'Benchmark_Weight': [np.sum(benchmark_weights)],
        'Active_Weight': [0],
        'Portfolio_Return': [R_P],
        'Benchmark_Return': [R_B],
        'Allocation_Effect': [np.sum(allocation_effect)],
        'Selection_Effect': [np.sum(selection_effect)],
        'Interaction_Effect': [np.sum(interaction_effect)],
        'Total_Effect': [R_P - R_B]
    })

    results = pd.concat([results, total_row], ignore_index=True)

    # 验证
    assert abs(results.iloc[-1]['Total_Effect'] - (R_P - R_B)) < 1e-10, \
        "归因加总与超额收益不一致"

    return results
