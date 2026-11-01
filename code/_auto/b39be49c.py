# @quantlab/output: b39be49c
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def pca_factor_compression(factor_df, n_components=None, variance_threshold=0.90):
    """
    使用PCA压缩因子，构建元因子

    factor_df: DataFrame, columns=因子名, index=股票
    n_components: 保留的主成分数（None则自动选择）
    variance_threshold: 方差解释阈值（自动选择时使用）
    """
    # 1. 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(factor_df)

    # 2. 拟合PCA
    if n_components is None:
        pca_full = PCA()
        pca_full.fit(X_scaled)
        cum_var = np.cumsum(pca_full.explained_variance_ratio_)
        n_components = np.searchsorted(cum_var, variance_threshold) + 1

    pca = PCA(n_components=n_components)
    meta_factors = pca.fit_transform(X_scaled)

    # 3. 解释各主成分
    loadings = pd.DataFrame(
        pca.components_.T,
        index=factor_df.columns,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )

    # 分析每个主成分的主要贡献因子
    print(f"因子数从 {factor_df.shape[1]} 压缩到 {n_components} 个元因子")
    print(f"累计解释方差: {pca.explained_variance_ratio_.sum():.2%}\n")

    for i in range(n_components):
        pc_loading = loadings[f'PC{i+1}']
        top_positive = pc_loading.nlargest(3)
        top_negative = pc_loading.nsmallest(3)
        print(f"PC{i+1} (解释方差 {pca.explained_variance_ratio_[i]:.1%}):")
        print(f"  正向载荷: {dict(top_positive)}")
        print(f"  负向载荷: {dict(top_negative)}")

    meta_factors_df = pd.DataFrame(
        meta_factors,
        index=factor_df.index,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )

    return meta_factors_df, loadings, pca

# ===== 示例 =====
np.random.seed(42)
n_stocks = 200
n_factors = 30

# 模拟因子数据（许多因子高度相关）
base_factors = np.random.randn(n_stocks, 3)  # 只有3个真实驱动
noise = np.random.randn(n_stocks, n_factors) * 0.3

factor_data = np.zeros((n_stocks, n_factors))
for i in range(n_factors):
    w1 = np.random.uniform(-1, 1)
    w2 = np.random.uniform(-1, 1)
    w3 = np.random.uniform(-1, 1)
    factor_data[:, i] = (w1 * base_factors[:, 0] +
                         w2 * base_factors[:, 1] +
                         w3 * base_factors[:, 2] + noise[:, i])

factor_df = pd.DataFrame(
    factor_data,
    index=[f'Stock_{i:04d}' for i in range(n_stocks)],
    columns=[f'Factor_{i:02d}' for i in range(n_factors)]
)

meta_factors, loadings, pca_model = pca_factor_compression(factor_df)
