# @quantlab/output: 998cfc62
def find_early_exercise_boundary(S0, K, T, r, sigma, n_steps):
    """计算美式看跌期权的最优行权边界"""
    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    boundary = []
    times = []

    # 在每个时间步查找使持有价值=行权价值的临界价格
    for step in range(n_steps):
        t = step * dt
        S = np.array([S0 * (u ** (step - i)) * (d ** i) for i in range(step + 1)])
        V = np.zeros(step + 1)
        for i in range(step + 1):
            V[i] = max(K - S[i], 0)
        # 此处为简化示意，完整实现需反向递推
        boundary.append(S[np.argmax(V > 0)])
        times.append(t)

    return times, boundary
