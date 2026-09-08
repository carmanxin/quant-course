# @quantlab/output: 1a72661f
def asian_option_mc(S0, K, T, r, sigma, n_avg_points=12, n_paths=100000):
    """亚式期权蒙特卡洛定价（算术平均）"""
    n_steps = n_avg_points
    dt = T / n_steps
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0

    for t in range(1, n_steps + 1):
        Z = np.random.randn(n_paths)
        S[:, t] = S[:, t-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

    avg_price = S[:, 1:].mean(axis=1)  # 算术平均
    payoff = np.maximum(avg_price - K, 0)
    price = np.exp(-r * T) * payoff.mean()
    return price

print(f"Asian Call Price: {asian_option_mc(100, 100, 1.0, 0.03, 0.20):.4f}")
