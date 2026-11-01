# @quantlab/output: 8c252caa
def lsm_american_put(S0, K, T, r, sigma, n_paths=10000, n_steps=50):
    """
    Longstaff-Schwartz 最小二乘蒙特卡洛 —— 美式看跌期权定价
    """
    dt = T / n_steps
    disc = np.exp(-r * dt)

    # 生成所有价格路径
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0
    for t in range(1, n_steps + 1):
        Z = np.random.randn(n_paths)
        S[:, t] = S[:, t-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

    # 初始 payoff（终端行权价值）
    V = np.maximum(K - S[:, -1], 0)

    # 逐时间步向后递推
    for t in range(n_steps - 1, 0, -1):
        V = V * disc  # 贴现到当前时间步

        # 当前标的价
        St = S[:, t]

        # 仅对实值期权进行回归（裁剪以加速）
        itm = np.where(St < K)[0]

        if len(itm) < 10:
            continue

        # 基函数：1, S, S^2
        X = np.column_stack([
            np.ones(len(itm)),
            St[itm],
            St[itm]**2
        ])

        # 对持有价值进行回归
        Y = V[itm]
        try:
            beta = np.linalg.lstsq(X, Y, rcond=None)[0]
            continuation_value = X @ beta
        except np.linalg.LinAlgError:
            continuation_value = np.zeros(len(itm))

        # 立即行权价值
        exercise_value = K - St[itm]

        # 选择最优策略
        exercise = exercise_value > continuation_value
        V[itm[exercise]] = exercise_value[exercise]
        V[itm[~exercise]] = V[itm[~exercise]]

    return V.mean() * disc

# LSM 定价示例
from scipy.stats import norm

S0, K, T, r, sigma = 100, 100, 1.0, 0.03, 0.25

lsm_price = lsm_american_put(S0, K, T, r, sigma, n_paths=50000, n_steps=50)
bs_eu_price = (
    K*np.exp(-r*T)*norm.cdf(-(np.log(S0/K)+(r-sigma**2/2)*T)/(sigma*np.sqrt(T)))
    - S0*norm.cdf(-(np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T)))
)

print(f"LSM 美式看跌: {lsm_price:.4f}")
print(f"BS 欧式看跌: {bs_eu_price:.4f}")
print(f"美式溢价: {lsm_price - bs_eu_price:.4f}")
