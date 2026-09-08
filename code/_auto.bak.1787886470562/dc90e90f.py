# @quantlab/output: dc90e90f
import numpy as np
import matplotlib.pyplot as plt

def optimal_trajectory_ac(total_qty, T, n_steps, sigma, eta, gamma, lam):
    """
    Almgren-Chriss 最优执行轨迹

    参数:
        total_qty: 总交易量
        T: 总时间（以天为单位）
        n_steps: 时间步数
        sigma: 资产波动率（年化）
        eta: 临时冲击系数
        gamma: 永久冲击系数
        lam: 风险厌恶系数（lambda）
    """
    dt = T / n_steps
    kappa = np.sqrt(lam * sigma**2 / eta)

    time_grid = np.linspace(0, T, n_steps + 1)
    trajectory = []

    for t in time_grid:
        if kappa * T > 0:  # 避免除零
            x_t = total_qty * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)
        else:
            x_t = total_qty * (1 - t / T)  # 退化为线性（TWAP）
        trajectory.append(x_t)

    return np.array(time_grid), np.array(trajectory)

# 参数设定
X = 100000         # 卖出10万股
T_days = 1         # 1个交易日
sigma_annual = 0.30  # 30%年化波动率
eta_val = 2e-6     # 临时冲击系数
gamma_val = 1e-6   # 永久冲击系数

# 不同风险厌恶参数下的最优轨迹
print("不同风险厌恶参数下的最优执行策略:")
print("-" * 55)
print(f"{'Lambda':>8} {'策略特点':>35} {'初始速率':>10}")
print("-" * 55)

strategies = [
    (0.001, '极低风险厌恶 → 极平缓执行'),
    (0.01, '低风险厌恶 → 较平缓执行'),
    (0.1, '中等风险厌恶 → 均衡执行'),
    (1.0, '高风险厌恶 → 快速执行'),
    (10.0, '极高风险厌恶 → 近乎市价单'),
]

for lam, desc in strategies:
    _, traj = optimal_trajectory_ac(X, T_days, 100, sigma_annual, eta_val, gamma_val, lam)
    initial_sell_rate = (X - traj[1]) / (T_days / 100)
    print(f"{lam:>8.3f} {desc:>35} {initial_sell_rate:>10.0f}")
