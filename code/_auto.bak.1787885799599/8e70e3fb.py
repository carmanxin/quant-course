# @quantlab/output: 8e70e3fb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import squareform
# 注:本案例纯 matplotlib + scipy, 不依赖 seaborn(浏览器沙箱不支持)。

def correlation_clustering(returns_df, method='ward', n_clusters=4):
    """
    基于相关性的层次聚类，识别资产群组

    returns_df: 每列是一只资产的收益率序列
    """
    # 计算相关系数矩阵
    corr_matrix = returns_df.corr()

    # 将相关系数转换为距离（1 - |corr| 或直接 1 - corr）
    # 注意：负相关也可以用于对冲到同一群组中
    distance_matrix = 1 - corr_matrix.abs()  # 负相关也视为相关
    # distance_matrix = 1 - corr_matrix  # 如果只想聚类正相关的资产

    # 层次聚类
    condensed_dist = squareform(distance_matrix.values)
    linkage_matrix = linkage(condensed_dist, method=method)

    # 生成聚类标签
    cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')

    # 按聚类排序
    sorted_idx = np.argsort(cluster_labels)
    sorted_corr = corr_matrix.iloc[sorted_idx, sorted_idx]
    sorted_labels = cluster_labels[sorted_idx]

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # 左：聚类后的相关性热力图(纯 matplotlib, 无需 seaborn)
    ax_left = axes[0]
    mask = np.triu(np.ones_like(sorted_corr, dtype=bool), k=1)
    arr = sorted_corr.values
    masked_arr = np.where(mask, np.nan, arr)
    im = ax_left.imshow(masked_arr, cmap='RdBu_r', vmin=-1, vmax=1,
                        aspect='equal', interpolation='nearest')
    cbar = plt.colorbar(im, ax=ax_left, shrink=0.8, fraction=0.046, pad=0.04)
    cbar.set_label('相关系数')
    ax_left.set_xticks([])
    ax_left.set_yticks([])

    # 添加聚类分隔线
    boundaries = np.where(np.diff(sorted_labels))[0]
    for b in boundaries:
        axes[0].axhline(y=b+1, color='black', linewidth=2)
        axes[0].axvline(x=b+1, color='black', linewidth=2)
    axes[0].set_title(f'资产相关性矩阵（层次聚类, n={n_clusters}）')

    # 右：树状图
    dendro = dendrogram(linkage_matrix, labels=returns_df.columns.tolist(),
                        ax=axes[1], orientation='left',
                        leaf_font_size=9)
    axes[1].set_title(f'层次聚类树状图 ({method} linkage)')
    axes[1].set_xlabel('距离 (1 - |corr|)')

    plt.tight_layout()
    plt.show()

    # 输出每个聚类的成员
    print("=== 聚类结果 ===")
    for c in range(1, n_clusters + 1):
        members = returns_df.columns[cluster_labels == c].tolist()
        print(f"聚类 {c} ({len(members)}个资产): {members[:5]}{'...' if len(members) > 5 else ''}")

    return {
        'corr_matrix': corr_matrix,
        'cluster_labels': cluster_labels,
        'linkage_matrix': linkage_matrix,
        'distance_matrix': distance_matrix
    }

# 一键运行(用 4 个因子 + df['returns'] 构造 5 列资产收益矩阵)
_np.random.seed(7)
_aligned_factors = factors.iloc[:len(df)]  # 因子行数与 df 对齐
_demo_returns = pd.DataFrame({
    'Asset_A':   df['returns'].values + _np.random.normal(0, 0.001, len(df)),
    'Asset_B':   0.7 * df['returns'].values + 0.3 * _aligned_factors['momentum'].values + _np.random.normal(0, 0.002, len(df)),
    'Asset_C':   0.6 * df['returns'].values + 0.4 * _aligned_factors['value'].values    + _np.random.normal(0, 0.002, len(df)),
    'Asset_D':   _aligned_factors['momentum'].values + _np.random.normal(0, 0.003, len(df)),
    'Asset_E':  -0.5 * _aligned_factors['momentum'].values + _np.random.normal(0, 0.003, len(df)),  # 与 D 负相关
}, index=df.index).iloc[1:]   # 去掉首个 NaN

results = correlation_clustering(_demo_returns, n_clusters=4)
print()
print(f"✅ 已识别 {results['cluster_labels'].max()} 个聚类群组")
