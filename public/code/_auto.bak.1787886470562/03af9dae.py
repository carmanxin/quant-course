# @quantlab/output: 03af9dae
def crisis_correlation_analysis(asset_returns: pd.DataFrame,
                                 crisis_dates: list = None) -> dict:
    """
    分析正常时期 vs 危机时期的跨资产相关性变化。

    参数:
        asset_returns: 各资产的日收益率
        crisis_dates: 危机期间的日期列表
    返回:
        包含正常和危机时期相关性矩阵的字典
    """
    if crisis_dates is None:
        # 示例：2008金融危机和2020新冠
        crisis_dates = [
            ('2008-09-01', '2009-03-31'),
            ('2020-02-19', '2020-03-23')
        ]

    # 正常时期（排除危机）
    crisis_mask = pd.Series(False, index=asset_returns.index)
    for start, end in crisis_dates:
        crisis_mask |= (asset_returns.index >= start) & \
                        (asset_returns.index <= end)

    normal_returns = asset_returns[~crisis_mask]
    crisis_returns = asset_returns[crisis_mask]

    # 计算相关性
    normal_corr = normal_returns.corr()
    crisis_corr = crisis_returns.corr()

    # 相关性差异
    corr_diff = crisis_corr - normal_corr

    # 可视化
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    titles = ['正常时期', '危机时期', '差异 (危机 - 正常)']
    matrices = [normal_corr, crisis_corr, corr_diff]

    for i, (title, mat) in enumerate(zip(titles, matrices)):
        im = axes[i].imshow(mat.values, cmap='RdBu_r',
                            vmin=-1, vmax=1, aspect='auto')
        axes[i].set_xticks(range(len(mat.columns)))
        axes[i].set_yticks(range(len(mat.columns)))
        axes[i].set_xticklabels(mat.columns, rotation=45, ha='right',
                                 fontsize=8)
        axes[i].set_yticklabels(mat.columns, fontsize=8)
        axes[i].set_title(title)
        plt.colorbar(im, ax=axes[i], shrink=0.8)

    plt.tight_layout()
    plt.show()

    # 相关性分散度：危机期间各资产间相关性趋于1
    normal_dispersion = np.std(normal_corr.values[np.triu_indices_from(
        normal_corr.values, k=1)])
    crisis_dispersion = np.std(crisis_corr.values[np.triu_indices_from(
        crisis_corr.values, k=1)])

    return {
        'normal_correlation': normal_corr,
        'crisis_correlation': crisis_corr,
        'correlation_diff': corr_diff,
        'dispersion_normal': normal_dispersion,
        'dispersion_crisis': crisis_dispersion,
        'diversification_benefit_deterioration': (
            normal_dispersion - crisis_dispersion
        ) / normal_dispersion * 100
    }
