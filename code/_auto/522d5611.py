# @quantlab/output: 522d5611
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def build_macro_factors_pca(economic_data: pd.DataFrame,
                              n_factors: int = 5) -> tuple:
    """
    通过PCA从经济数据中提取宏观因子。

    参数:
        economic_data: 经济指标DataFrame，行=时间，列=指标
        n_factors: 提取的主成分数量
    返回:
        (factors, loadings, explained_variance)
    """
    # 标准化
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(economic_data)

    # PCA
    pca = PCA(n_components=n_factors)
    factors = pca.fit_transform(data_scaled)

    # 因子载荷
    loadings = pd.DataFrame(
        pca.components_.T,
        index=economic_data.columns,
        columns=[f'Factor{i+1}' for i in range(n_factors)]
    )

    # 解释方差
    explained_variance = pca.explained_variance_ratio_

    # 命名因子（基于最大载荷的经济指标）
    factor_names = []
    for i in range(n_factors):
        top_indicator = loadings[f'Factor{i+1}'].abs().idxmax()
        factor_names.append(f'PC{i+1} ({top_indicator})')

    factors_df = pd.DataFrame(
        factors,
        index=economic_data.index,
        columns=factor_names
    )

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 解释方差
    axes[0, 0].bar(range(1, n_factors + 1),
                   explained_variance * 100, color='steelblue')
    axes[0, 0].plot(range(1, n_factors + 1),
                    np.cumsum(explained_variance) * 100,
                    'ro-', markersize=8)
    axes[0, 0].set_xlabel('主成分')
    axes[0, 0].set_ylabel('解释方差 (%)')
    axes[0, 0].set_title('各主成分解释方差')
    axes[0, 0].grid(True, alpha=0.3)

    # 载荷热力图（前两个因子）
    load_top = loadings.iloc[:, :2].copy()
    load_top = load_top.loc[load_top.abs().sum(axis=1).sort_values(
        ascending=False).index[:15]]

    im = axes[0, 1].imshow(load_top.values, cmap='RdBu_r', aspect='auto',
                           vmin=-1, vmax=1)
    axes[0, 1].set_xticks(range(2))
    axes[0, 1].set_xticklabels(load_top.columns)
    axes[0, 1].set_yticks(range(len(load_top)))
    axes[0, 1].set_yticklabels(load_top.index, fontsize=8)
    axes[0, 1].set_title('前两个因子的载荷')
    plt.colorbar(im, ax=axes[0, 1])

    # 因子时序
    for i, col in enumerate(factors_df.columns[:2]):
        axes[1, i].plot(factors_df.index, factors_df[col],
                        linewidth=1, color=['darkblue', 'darkred'][i])
        axes[1, i].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[1, i].set_title(col)
        axes[1, i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    return factors_df, loadings, explained_variance

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(42)
_demo_dates = pd.date_range('2015-01-31', periods=120, freq='ME')
_demo_growth = np.cumsum(np.random.randn(120) * 0.3)
_demo_infl = 2 + np.cumsum(np.random.randn(120) * 0.2)
_economic_data = pd.DataFrame({
    '工业增加值同比': 6 + _demo_growth * 0.5 + np.random.randn(120) * 0.3,
    'CPI同比': _demo_infl + np.random.randn(120) * 0.1,
    'PPI同比': _demo_infl * 1.2 - 1 + np.random.randn(120) * 0.5,
    '社融存量同比': 10 + _demo_growth * 0.4 + np.random.randn(120) * 0.4,
    'PMI': 50 + _demo_growth * 0.8 + np.random.randn(120) * 0.5,
    '出口同比': 5 + _demo_growth * 1.2 + np.random.randn(120) * 1.5,
}, index=_demo_dates)
_factors_df, _loadings, _ev = build_macro_factors_pca(_economic_data, n_factors=3)
print('解释方差比:', np.round(_ev, 3))
