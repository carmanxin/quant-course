# @quantlab/output: 792432ba
from scipy.linalg import solve_banded

def implicit_fdm(S0, K, T, r, sigma, S_max, n_S, n_T, option_type='put'):
    """
    隐式有限差分法 —— 欧式期权定价
    S_max: 截断的标的价格上界 (通常 2-3x S0)
    n_S: 价格网格数
    n_T: 时间网格数
    """
    dS = S_max / n_S
    dt = T / n_T
    S = np.linspace(0, S_max, n_S + 1)

    # 终端条件
    if option_type == 'call':
        V = np.maximum(S - K, 0)
    else:
        V = np.maximum(K - S, 0)

    # 边界条件
    # 构建三对角矩阵的系数
    for j in range(n_T, 0, -1):
        a = np.zeros(n_S - 1)
        b = np.zeros(n_S - 1)
        c = np.zeros(n_S - 1)
        d = np.zeros(n_S - 1)

        for i in range(1, n_S):
            Si = i * dS
            a[i-1] = 0.5 * dt * (r * i - sigma**2 * i**2)
            b[i-1] = 1 + dt * (sigma**2 * i**2 + r)
            c[i-1] = -0.5 * dt * (sigma**2 * i**2 + r * i)
            d[i-1] = V[i]

        # 边界条件修正
        if option_type == 'call':
            d[-1] -= c[-1] * (S_max - K * np.exp(-r * (T - j * dt)))
        else:
            d[0] -= a[0] * (K * np.exp(-r * (T - j * dt)))

        # 求解三对角系统
        ab = np.zeros((3, n_S - 1))
        ab[0, 1:] = c[:-1]
        ab[1, :] = b
        ab[2, :-1] = a[1:]

        V[1:n_S] = solve_banded((1, 1), ab, d)

        # 重新应用边界条件
        if option_type == 'call':
            V[0] = 0
            V[n_S] = S_max - K * np.exp(-r * (T - j * dt))
        else:
            V[0] = K * np.exp(-r * (T - j * dt))
            V[n_S] = 0

    # 查找 S0 对应的期权价格
    idx = int(S0 / dS)
    return V[idx] + (V[idx+1] - V[idx]) * (S0 - S[idx]) / dS
