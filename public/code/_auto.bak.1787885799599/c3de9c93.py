# @quantlab/output: c3de9c93
import numpy as np
import matplotlib.pyplot as plt

def simulate_limit_order_fill_prob(S0, K, mu, sigma, T, n_steps, n_simulations):
    """
    蒙特卡洛模拟限价单的成交概率

    参数:
        S0: 当前价格
        K: 限价（对于买单，K < S0，希望价格下跌到K时成交）
        mu: 漂移率
        sigma: 波动率
        T: 时间窗口（年）
        n_steps: 时间步数
        n_simulations: 模拟路径数
    """
    dt = T / n_steps
    fills = np.zeros(n_simulations)

    for i in range(n_simulations):
        S = S0
        for t in range(n_steps):
            dW = np.random.normal(0, np.sqrt(dt))
            S *= np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * dW)
            if S <= K:  # 买单成交条件
                fills[i] = 1
                break

    fill_prob = fills.mean()
    avg_fill_time = np.where(fills == 1)[0].size  # simplified
    return fill_prob

# 参数设定
S0 = 100.0
mu = 0.05
sigma = 0.30
T = 1/252  # 1个交易日

# 测试不同价差下的成交概率
print("限价单成交概率模拟（1日窗口）:")
print("-" * 50)
for spread_bp in [1, 5, 10, 20, 50, 100]:
    K = S0 * (1 - spread_bp / 10000)
    prob = simulate_limit_order_fill_prob(S0, K, mu, sigma, T,
                                           n_steps=390, n_simulations=5000)
    print(f"价差 {spread_bp:3d}bp (挂单价={K:.4f}): 成交概率 = {prob:.2%}")
