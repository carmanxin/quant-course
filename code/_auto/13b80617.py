# @quantlab/output: 13b80617
import numpy as np

def correlation_breakdown_stress(correlation_matrix: np.ndarray,
                                  volatilities: np.ndarray,
                                  crisis_multiplier: float = 3.0) -> np.ndarray:
    """
    生成相关性破裂的极端压力协方差矩阵。

    在极端压力下，所有相关性向 ±1 收缩，
    同时波动率放大。

    参数:
        correlation_matrix: 正常时期的相关系数矩阵
        volatilities: 正常时期的波动率
        crisis_multiplier: 波动率放大倍数
    返回:
        极端压力下的协方差矩阵
    """
    n = len(volatilities)

    # 相关性破裂：向 +1 收缩
    crisis_corr = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                # 相关性向 1 收缩 80%
                crisis_corr[i, j] = correlation_matrix[i, j] * 0.2 + 0.8

    # 波动率放大
    crisis_vol = volatilities * crisis_multiplier

    # 协方差矩阵
    D = np.diag(crisis_vol)
    crisis_cov = D @ crisis_corr @ D

    return crisis_cov


def multi_asset_stress_pnl(positions: np.ndarray,
                            normal_cov: np.ndarray,
                            confidence: float = 0.999,
                            n_simulations: int = 10000) -> dict:
    """
    多资产联动压力测试：模拟极端市场条件下的P&L分布。

    使用 Copula 或 t-Copula 捕捉极端事件间的尾部依赖。

    参数:
        positions: 各头寸的市场价值
        normal_cov: 正常时期的协方差矩阵
        confidence: 极端情景的置信水平
        n_simulations: 蒙特卡洛模拟次数
    返回:
        压力测试结果
    """
    n_assets = len(positions)

    # 使用 t-Copula 生成尾部相依的随机冲击
    df_t = 3  # 自由度越低，尾部相依性越强
    vol = np.sqrt(np.diag(normal_cov))
    corr = normal_cov / np.outer(vol, vol)

    # t-Copula 模拟
    np.random.seed(42)
    z = np.random.randn(n_simulations, n_assets)
    chi = np.random.chisquare(df_t, n_simulations) / df_t
    t_samples = z / np.sqrt(chi[:, np.newaxis])  # 多元 t 分布

    # 映射到收益率
    L = np.linalg.cholesky(corr)
    correlated_t = t_samples @ L.T

    # 极端情景：取 t 分布的极端分位数
    extreme_returns = np.percentile(correlated_t, (1 - confidence) * 100, axis=0)

    # P&L
    pnl_vector = positions * extreme_returns * vol
    total_pnl = np.sum(pnl_vector)

    return {
        'total_pnl_impact': total_pnl,
        'asset_level_impacts': dict(zip(
            [f'Asset_{i}' for i in range(n_assets)], pnl_vector
        )),
        'pct_of_portfolio': total_pnl / np.sum(np.abs(positions)) * 100
    }

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_corr = np.array([
    [1.0, -0.3, 0.4, 0.2],
    [-0.3, 1.0, -0.1, -0.2],
    [0.4, -0.1, 1.0, 0.5],
    [0.2, -0.2, 0.5, 1.0],
])
_vols = np.array([0.15, 0.08, 0.25, 0.20])
_cb = correlation_breakdown_stress(_corr, _vols, crisis_multiplier=3.0)
print(np.round(_cb, 3))


# ===== 合成数据最小示例: 多资产联动压力（数据为模拟，机制真实）=====
np.random.seed(191)
_A5 = np.random.randn(4, 300)
_cov5 = np.cov(_A5) * 0.02
_pos5 = np.array([1e6, 2e6, -5e5, 8e5])
_mp = multi_asset_stress_pnl(_pos5, _cov5)
for _k, _v in _mp.items():
    print(_k, ':', _v if np.isscalar(_v) else (np.round(_v, 2) if isinstance(_v, np.ndarray) else _v))
