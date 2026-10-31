# @quantlab/output: 2928d335
def performance_attribution(returns: pd.DataFrame, weights: np.ndarray) -> Dict[str, float]:
    """Brinson 模型简化版:策略贡献分解"""
    p_returns = returns @ weights
    n = len(returns.columns)

    contribution = {}
    for i, col in enumerate(returns.columns):
        # 每个策略的"加权累积贡献"
        cumulative_contrib = (returns[col] * weights[i]).sum()
        contribution[col] = cumulative_contrib

    total = sum(contribution.values())
    print(f"\n策略贡献度(% of 总贡献):")
    for col, contrib in contribution.items():
        pct = contrib / total if total != 0 else 0
        print(f"  {col}: {pct:.2%}")

    # 时间贡献:每个月哪个策略赚钱最多
    monthly_contrib = returns.apply(lambda x: x * weights[returns.columns.get_loc(x.name)])
    monthly_winner = monthly_contrib.idxmax(axis=1).value_counts()
    print(f"\n每月最佳策略次数:")
    for k, v in monthly_winner.items():
        print(f"  {k}: {v} 次")

    return contribution


print("=" * 60)
print("性能归因:3 个策略组合的贡献")
print("=" * 60)
contribution = performance_attribution(returns_df, np.array([1/3]*3))
