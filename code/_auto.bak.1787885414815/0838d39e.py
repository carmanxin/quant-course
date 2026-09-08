# @quantlab/output: 0838d39e
def equal_weight_allocation(n_strategies: int) -> np.ndarray:
    """等权分配"""
    return np.array([1.0 / n_strategies] * n_strategies)


def risk_parity_allocation(returns: pd.DataFrame) -> np.ndarray:
    """风险平价分配:权重 ∝ 1/σ(波动率的倒数)"""
    volatilities = returns.std() * np.sqrt(252)
    inverse_vol = 1.0 / volatilities
    weights = inverse_vol / inverse_vol.sum()
    return weights.values


def max_sharpe_allocation(returns: pd.DataFrame, risk_free: float = 0.025) -> np.ndarray:
    """最大夏普分配:Markowitz 优化
    注意:实盘中需用 Ledoit-Wolf 收缩,这里用 sklearn-标准实现
    """
    from scipy.optimize import minimize

    mu = returns.mean() * 252 - risk_free
    cov = returns.cov() * 252

    n = len(mu)
    def neg_sharpe(w):
        p_ret = w @ mu
        p_vol = np.sqrt(w @ cov @ w)
        return -p_ret / (p_vol + 1e-9)

    # 约束:权重和为1,每个权重在 [0, 0.5]
    constraints = [{'type': 'eq', 'fun': lambda w: w.sum() - 1}]
    bounds = [(0, 0.5)] * n

    result = minimize(
        neg_sharpe,
        x0=np.array([1/n] * n),
        bounds=bounds,
        constraints=constraints,
        method='SLSQP'
    )
    return result.x


def kelly_allocation(returns: pd.DataFrame, fraction: float = 0.25) -> np.ndarray:
    """Kelly 公式分配(分数 Kelly,fraction=0.25 表示 1/4 Kelly)
    Kelly 的简化形式:w = μ / σ²,在多策略情况下用每个策略各自的 Kelly
    """
    mu = returns.mean() * 252
    var = returns.var() * 252
    kelly_weights = (mu / var).clip(lower=0)  # 不允许负权重(简化版)
    kelly_weights *= fraction
    kelly_weights /= kelly_weights.sum()  # 归一化
    return kelly_weights.values


# === 比较 4 种分配方法 ===
methods = {
    '等权 (1/N)': equal_weight_allocation(3),
    '风险平价': risk_parity_allocation(returns_df),
    '最大夏普': max_sharpe_allocation(returns_df),
    '分数 Kelly (0.25)': kelly_allocation(returns_df),
}

print("=" * 60)
print("4 种资金分配方法对比")
print("=" * 60)
print(f"{'方法':<20} {'Trend':>10} {'MeanRev':>10} {'LongShort':>10}")
print("-" * 60)
for name, weights in methods.items():
    print(f"{name:<20} {weights[0]:>10.2%} {weights[1]:>10.2%} {weights[2]:>10.2%}")


# === 计算每种组合的组合夏普 ===
def portfolio_sharpe(returns: pd.DataFrame, weights: np.ndarray) -> float:
    p_ret = returns @ weights
    ann_ret = p_ret.mean() * 252
    ann_vol = p_ret.std() * np.sqrt(252)
    return ann_ret / (ann_vol + 1e-9)


print("\n" + "=" * 60)
print("4 种分配方法下的组合夏普")
print("=" * 60)
for name, weights in methods.items():
    sharpe = portfolio_sharpe(returns_df, weights)
    print(f"  {name:<20}: {sharpe:.2f}")
