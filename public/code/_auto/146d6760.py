# @quantlab/output: 146d6760
import numpy as np

def barrier_option_mc(S0, K, H, T, r, sigma, barrier_type, n_paths=100000):
    """
    障碍期权蒙特卡洛定价
    S0: 初始价格
    K: 行权价
    H: 障碍水平
    T: 到期时间
    barrier_type: 'up-out-call', 'down-out-put', etc.
    """
    np.random.seed(42)
    n_steps = 252  # 日频模拟
    dt = T / n_steps

    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0
    is_active = np.ones(n_paths, dtype=bool)

    for t in range(1, n_steps + 1):
        Z = np.random.randn(n_paths)
        S[:, t] = S[:, t-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

        if 'up' in barrier_type:
            is_active &= (S[:, t] < H)
        elif 'down' in barrier_type:
            is_active &= (S[:, t] > H)

    # 计算Payoff
    ST = S[:, -1]

    if 'call' in barrier_type:
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)

    if 'out' in barrier_type:
        payoff *= is_active  # 敲出则失效
    elif 'in' in barrier_type:
        payoff *= (~is_active)  # 未敲入则失效

    return np.exp(-r * T) * payoff.mean(), payoff.std() / np.sqrt(n_paths)

# 示例
price, se = barrier_option_mc(
    S0=100, K=100, H=110, T=1.0, r=0.03, sigma=0.20,
    barrier_type='up-out-call', n_paths=50000
)
print(f"Up-and-Out Call Price: {price:.4f} ± {1.96*se:.4f} (95% CI)")
