# @quantlab/output: b8eced91
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Dict

# 设置全局参数
np.random.seed(42)
N_DAYS = 2520  # 10 年日线


def gbm_generator(n_days: int = N_DAYS,
                  mu: float = 0.0004,
                  sigma: float = 0.02,
                  s0: float = 100.0) -> pd.Series:
    """L1: 几何布朗运动(GBM)
    μ = 年化日收益 0.04%,σ = 年化日波动 31.6%
    """
    daily_returns = np.random.normal(
        loc=mu - 0.5 * sigma**2,
        scale=sigma,
        size=n_days
    )
    prices = s0 * np.exp(np.cumsum(daily_returns))
    return pd.Series(prices, name='GBM')


def heston_generator(n_days: int = N_DAYS,
                     mu: float = 0.0004,
                     s0: float = 100.0,
                     v0: float = 0.04**2,   # 初始年化方差
                     kappa: float = 2.0,    # 均值回归速度
                     theta: float = 0.04**2, # 长期方差
                     xi: float = 0.3,        # vol of vol
                     rho: float = -0.7) -> pd.Series:
    """L2: Heston 随机波动率模型

    使用 Euler-Maruyama 离散化:
    v_{t+1} = v_t + κ(θ - v_t)Δt + ξ √(v_t) √Δt Z_v
    S_{t+1} = S_t exp((μ - 0.5v_t)Δt + √(v_t)Δt (ρ Z_v + √(1-ρ²) Z_s))
    """
    dt = 1 / 252
    sqrt_dt = np.sqrt(dt)

    v = np.zeros(n_days)
    s = np.zeros(n_days)
    v[0] = v0
    s[0] = s0

    for t in range(1, n_days):
        z_v = np.random.normal()
        z_s = np.random.normal()
        v[t] = v[t-1] + kappa * (theta - v[t-1]) * dt + xi * np.sqrt(max(v[t-1], 0)) * sqrt_dt * z_v
        v[t] = max(v[t], 1e-8)  # 保证方差非负
        drift = (mu - 0.5 * v[t-1]) * dt
        diffusion_s = np.sqrt(v[t-1] * dt) * (rho * z_v + np.sqrt(1 - rho**2) * z_s)
        s[t] = s[t-1] * np.exp(drift + diffusion_s)

    return pd.Series(s, name='Heston')


def jump_diffusion_generator(n_days: int = N_DAYS,
                            mu: float = 0.0004,
                            sigma: float = 0.015,
                            s0: float = 100.0,
                            jump_lambda: float = 0.05,    # 年化 5% 概率
                            jump_mu: float = -0.05,
                            jump_sigma: float = 0.08) -> pd.Series:
    """L3: Jump Diffusion(Merton 模型)

    在 GBM 基础上加 Poisson 跳跃,捕捉黑天鹅事件
    """
    dt = 1 / 252
    daily_returns = np.zeros(n_days)
    for t in range(1, n_days):
        # GBM 扩散部分
        z = np.random.normal()
        diffusion = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z

        # 跳跃部分(以 Poisson 频率出现)
        n_jumps = np.random.poisson(jump_lambda * dt)
        if n_jumps > 0:
            jumps = sum(np.random.normal(jump_mu, jump_sigma) for _ in range(n_jumps))
        else:
            jumps = 0

        daily_returns[t] = diffusion + jumps

    prices = s0 * np.exp(np.cumsum(daily_returns))
    return pd.Series(prices, name='JumpDiff')


def bates_generator(n_days: int = N_DAYS,
                    mu: float = 0.0004,
                    s0: float = 100.0,
                    v0: float = 0.04**2,
                    kappa: float = 2.0,
                    theta: float = 0.04**2,
                    xi: float = 0.3,
                    rho: float = -0.7,
                    jump_lambda: float = 0.05,
                    jump_mu: float = -0.05,
                    jump_sigma: float = 0.08) -> pd.Series:
    """L4: Bates 模型(Heston + Jump,2-factor)
    最高保真度:同时支持随机波动率和跳跃
    """
    dt = 1 / 252
    sqrt_dt = np.sqrt(dt)

    v = np.zeros(n_days)
    s = np.zeros(n_days)
    v[0] = v0
    s[0] = s0

    for t in range(1, n_days):
        z_v = np.random.normal()

        # Heston 波动更新
        v[t] = v[t-1] + kappa * (theta - v[t-1]) * dt + xi * np.sqrt(max(v[t-1], 0)) * sqrt_dt * z_v
        v[t] = max(v[t], 1e-8)

        # 价格更新 + 跳跃
        z_s = np.random.normal()
        n_jumps = np.random.poisson(jump_lambda * dt)
        jump_sum = sum(np.random.normal(jump_mu, jump_sigma) for _ in range(n_jumps)) if n_jumps else 0

        drift = (mu - 0.5 * v[t-1]) * dt
        diffusion_s = np.sqrt(v[t-1] * dt) * (rho * z_v + np.sqrt(1 - rho**2) * z_s)
        s[t] = s[t-1] * np.exp(drift + diffusion_s + jump_sum)

    return pd.Series(s, name='Bates')


def compute_statistics(prices: pd.Series) -> Dict[str, float]:
    """计算一组价格序列的核心统计特征"""
    returns = prices.pct_change().dropna()
    vol = prices.diff().apply(np.log).dropna().std() * np.sqrt(252)
    return {
        '均值(年化)': f"{returns.mean() * 252 * 100:.2f}%",
        '波动(年化)': f"{vol * 100:.2f}%",
        '偏度': f"{returns.skew():.2f}",
        '峰度': f"{returns.kurtosis():.2f}",
        '最大回撤': f"{(prices / prices.cummax() - 1).min() * 100:.2f}%",
        '夏普(0%)': f"{(returns.mean() / returns.std()) * np.sqrt(252):.2f}",
    }


# === 演示运行 ===
print("=" * 60)
print("4 种合成数据生成器性能测试")
print("=" * 60)

gbm_series = gbm_generator()
print(f"GBM 生成 {len(gbm_series)} 个点:OK")

heston_series = heston_generator()
print(f"Heston 生成 {len(heston_series)} 个点:OK")

jd_series = jump_diffusion_generator()
print(f"JumpDiff 生成 {len(jd_series)} 个点:OK")

bates_series = bates_generator()
print(f"Bates 生成 {len(bates_series)} 个点:OK")

print("\n" + "=" * 60)
print("统计特征对比")
print("=" * 60)
stats = {
    'GBM': compute_statistics(gbm_series),
    'Heston': compute_statistics(heston_series),
    'JumpDiff': compute_statistics(jd_series),
    'Bates': compute_statistics(bates_series),
}
stats_df = pd.DataFrame(stats).T
print(stats_df)
