# @quantlab/output: 20d6ad30
import numpy as np

def crr_binomial_tree(S0, K, T, r, sigma, n_steps, option_type='call', american=False):
    """
    CRR 二叉树期权定价
    american=True 时支持提前行权（美式期权）
    """
    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    # 初始化终端价格
    S = np.zeros(n_steps + 1)
    V = np.zeros(n_steps + 1)

    for i in range(n_steps + 1):
        S[i] = S0 * (u ** (n_steps - i)) * (d ** i)
        if option_type == 'call':
            V[i] = max(S[i] - K, 0)
        else:
            V[i] = max(K - S[i], 0)

    # 向后递推
    for step in range(n_steps - 1, -1, -1):
        for i in range(step + 1):
            S[i] = S0 * (u ** (step - i)) * (d ** i)
            # 持有价值（风险中性期望的贴现值）
            hold_value = disc * (p * V[i] + (1 - p) * V[i + 1])

            if american:
                # 美式期权：取持有价值和立即行权价值的最大值
                if option_type == 'call':
                    exercise_value = S[i] - K
                else:
                    exercise_value = K - S[i]
                V[i] = max(hold_value, exercise_value)
            else:
                V[i] = hold_value

    return V[0]


# 欧式与美式期权定价对比
S0, K, T, r, sigma, n = 100, 100, 1.0, 0.03, 0.25, 200

eu_call = crr_binomial_tree(S0, K, T, r, sigma, n, 'call', american=False)
am_call = crr_binomial_tree(S0, K, T, r, sigma, n, 'call', american=True)
eu_put = crr_binomial_tree(S0, K, T, r, sigma, n, 'put', american=False)
am_put = crr_binomial_tree(S0, K, T, r, sigma, n, 'put', american=True)

print(f"欧式看涨: {eu_call:.4f}  |  美式看涨: {am_call:.4f}")
print(f"欧式看跌: {eu_put:.4f}  |  美式看跌: {am_put:.4f}")
