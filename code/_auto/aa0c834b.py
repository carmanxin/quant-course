# @quantlab/output: aa0c834b
def lookback_option_mc(S0, T, r, sigma, option_type='call', n_paths=100000):
    """回望期权蒙特卡洛定价"""
    n_steps = 252
    dt = T / n_steps
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0

    for t in range(1, n_steps + 1):
        Z = np.random.randn(n_paths)
        S[:, t] = S[:, t-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

    if option_type == 'call':
        payoff = S[:, -1] - S[:, 1:].min(axis=1)
    else:
        payoff = S[:, 1:].max(axis=1) - S[:, -1]

    return np.exp(-r * T) * payoff.mean()
