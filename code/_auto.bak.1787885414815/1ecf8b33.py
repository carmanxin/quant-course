# @quantlab/output: 1ecf8b33
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from typing import Callable

def ac_optimal_trajectory(X: float,
                           T: float,
                           N: int,
                           sigma: float,
                           gamma: float,
                           eta: float,
                           risk_aversion: float) -> np.ndarray:
    """
    Almgren-Chriss 最优执行轨迹的闭式解（线性冲击假设）。

    参数:
        X: 总执行量
        T: 总执行时间（分钟）
        N: 时间步数
        sigma: 年化波动率
        gamma: 永久冲击系数（bps / 份额）
        eta: 临时冲击系数（bps / 份额 / 时间）
        risk_aversion: 风险厌恶参数 λ
    返回:
        各时间点的剩余头寸 x_k 数组
    """
    tau = T / N
    kappa = np.sqrt(risk_aversion * sigma ** 2 / eta)

    t = np.linspace(0, T, N + 1)

    # 闭式解
    x = X * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)

    return x


def ac_execution_cost(x: np.ndarray,
                       X: float,
                       tau: float,
                       sigma: float,
                       gamma: float,
                       eta: float,
                       risk_aversion: float) -> dict:
    """
    计算给定执行轨迹的总成本及其分解。

    参数:
        x: 剩余头寸轨迹
        X: 总执行量
        tau: 时间步长
        sigma, gamma, eta: 模型参数
        risk_aversion: 风险厌恶参数
    返回:
        包含 total_cost, permanent_cost, temporary_cost, risk_cost 的字典
    """
    N = len(x) - 1
    n = np.diff(-x)  # 每步执行量: x_{k-1} - x_k

    # 永久冲击成本
    permanent_cost = gamma / 2 * X ** 2

    # 临时冲击成本
    temporary_cost = eta / tau * np.sum(n ** 2)

    # 期望执行成本
    expected_cost = permanent_cost + temporary_cost

    # 风险成本
    risk_cost = sigma ** 2 * tau * np.sum(x[1:] ** 2)

    # 效用 = 期望成本 + lambda * 方差
    total_utility = expected_cost + risk_aversion * risk_cost

    return {
        'total_utility': total_utility,
        'expected_cost': expected_cost,
        'permanent_cost': permanent_cost,
        'temporary_cost': temporary_cost,
        'risk_cost': risk_cost
    }
