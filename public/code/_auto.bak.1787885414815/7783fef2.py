# @quantlab/output: 7783fef2
import matplotlib.pyplot as plt
# 注:本案例纯 matplotlib + scipy, 不依赖 seaborn(浏览器沙箱不支持)。
import numpy as np
import pandas as pd
from scipy import stats

def factor_analysis_viz(factor_values, forward_returns, factor_name='Factor',
                         n_quantiles=5, periods=None):
    """
    因子分析可视化套件

    factor_values: Series, 每期的因子值
    forward_returns: Series, 对应的未来一期收益率
    """
    # 对齐数据
    data = pd.DataFrame({
        'factor': factor_values,
        'fwd_return': forward_returns
    }).dropna()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # === 1. 散点图+回归线 ===
    axes[0, 0].scatter(data['factor'], data['fwd_return'],
                      alpha=0.3, s=10, c='steelblue', edgecolors='none')

    # 添加分组均值线
    data['quantile'] = pd.qcut(data['factor'], n_quantiles, labels=False, duplicates='drop')
    group_means = data.groupby('quantile')[['factor', 'fwd_return']].mean()
    axes[0, 0].plot(group_means['factor'], group_means['fwd_return'],
                   'ro-', linewidth=2, markersize=8, label='分组均值')

    # OLS回归线
    slope, intercept, r_value, p_value, _ = stats.linregress(data['factor'], data['fwd_return'])
    x_range = np.linspace(data['factor'].min(), data['factor'].max(), 100)
    axes[0, 0].plot(x_range, intercept + slope * x_range, 'r-', linewidth=1.5,
                   alpha=0.5, label=f'OLS (R={r_value:.3f}, p={p_value:.4f})')

    axes[0, 0].axhline(y=0, color='black', linewidth=0.5, linestyle='--')
    axes[0, 0].set_xlabel('因子值')
    axes[0, 0].set_ylabel('未来收益')
    axes[0, 0].set_title(f'{factor_name}: 因子-收益散点图')
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)

    # === 2. 分位数收益柱状图 ===
    quantile_returns = data.groupby('quantile')['fwd_return'].mean()
    quantile_std = data.groupby('quantile')['fwd_return'].std() / np.sqrt(data.groupby('quantile').size())

    colors_bar = ['#e74c3c' if x < 0 else '#2ecc71' for x in quantile_returns]
    axes[0, 1].bar(range(len(quantile_returns)), quantile_returns.values,
                  color=colors_bar, edgecolor='white', yerr=quantile_std.values,
                  capsize=5, alpha=0.8)
    axes[0, 1].axhline(y=0, color='black', linewidth=0.5)
    axes[0, 1].set_xticks(range(len(quantile_returns)))
    axes[0, 1].set_xticklabels([f'Q{i+1}\n(低)' if i==0 else f'Q{i+1}\n(高)' if i==len(quantile_returns)-1 else f'Q{i+1}'
                                for i in range(len(quantile_returns))])
    axes[0, 1].set_ylabel('平均未来收益')
    axes[0, 1].set_title(f'{factor_name}: 分位数收益 (Q1-Q{n_quantiles})')
    axes[0, 1].grid(True, alpha=0.3)

    # === 3. Q-Q图 (因子值分布) ===
    stats.probplot(data['factor'], dist='norm', plot=axes[0, 2])
    axes[0, 2].set_title(f'{factor_name}: Q-Q图 (正态性检验)')
    axes[0, 2].grid(True, alpha=0.3)

    # === 4. 因子IC序列 (滚动) ===
    # 计算滚动Rank IC
    if len(data) > 60:
        rolling_ic = data['factor'].rolling(60).corr(data['fwd_return'])  # 默认 Pearson;若需 Spearman 改用 rolling(60).apply(lambda x: x.corr(x, method='spearman'))
        axes[1, 0].plot(rolling_ic.index, rolling_ic.values, linewidth=0.8, color='#2980b9')
        axes[1, 0].axhline(y=0, color='black', linewidth=0.5)
        axes[1, 0].axhline(y=rolling_ic.mean(), color='red', linestyle='--', linewidth=1,
                          label=f'均值={rolling_ic.mean():.4f}')
        axes[1, 0].fill_between(rolling_ic.index, 0, rolling_ic.values,
                               where=rolling_ic.values > 0, color='green', alpha=0.2)
        axes[1, 0].fill_between(rolling_ic.index, 0, rolling_ic.values,
                               where=rolling_ic.values < 0, color='red', alpha=0.2)
        axes[1, 0].set_title(f'{factor_name}: 滚动60期Rank IC')
        axes[1, 0].set_ylabel('Rank IC')
        axes[1, 0].legend(fontsize=8)
        axes[1, 0].grid(True, alpha=0.3)

    # === 5. 累积分位数收益 ===
    # 计算每个分位数的累计收益
    cum_returns = {}
    for q in sorted(data['quantile'].unique()):
        mask = data['quantile'] == q
        cum_rets = (1 + data.loc[mask, 'fwd_return'].sort_index()).cumprod()
        cum_returns[q] = cum_rets

    # 使用热力图展示不同时期的分位数收益
    if 'date' in data.columns:
        pass  # 可以用seaborn heatmap展示时间序列

    for q, cum_ret in cum_returns.items():
        label = f'Q{q+1}'
        alpha_val = 1.0 if q in [0, len(cum_returns)-1] else 0.3
        linewidth = 2 if q in [0, len(cum_returns)-1] else 0.5
        axes[1, 1].plot(cum_ret.index, cum_ret.values, linewidth=linewidth,
                       alpha=alpha_val, label=label)

    axes[1, 1].set_title(f'{factor_name}: 各分位数累计收益')
    axes[1, 1].set_ylabel('累计收益')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)

    # === 6. 因子分布 + 分组边界 ===
    axes[1, 2].hist(data['factor'], bins=50, density=True, color='steelblue',
                   alpha=0.6, edgecolor='white')

    # 标注分位数边界
    for q in range(1, n_quantiles):
        boundary = data['factor'].quantile(q / n_quantiles)
        axes[1, 2].axvline(x=boundary, color='red', linestyle='--',
                          linewidth=0.8, alpha=0.6)

    axes[1, 2].axvline(x=data['factor'].median(), color='red', linewidth=1.5,
                      label=f'中位数={data["factor"].median():.3f}')
    axes[1, 2].set_title(f'{factor_name}: 因子分布 (Q1-Q{n_quantiles}分位线)')
    axes[1, 2].legend(fontsize=8)
    axes[1, 2].grid(True, alpha=0.3)

    # 总标题
    fig.suptitle(f'因子分析: {factor_name}', fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.show()

    # 输出统计信息
    print("=" * 50)
    print(f"因子分析: {factor_name}")
    print("=" * 50)
    print(f"样本量: {len(data)}")
    print(f"Rank IC: {data['factor'].corr(data['fwd_return'], method='spearman'):.4f}")
    print(f"OLS斜率: {slope:.6f}, R={r_value:.4f}, p={p_value:.4f}")
    print(f"Q1-Q{n_quantiles} 超额收益: {quantile_returns.iloc[-1] - quantile_returns.iloc[0]:.6f}")

    # 单调性检验
    mono_violations = np.sum(np.diff(quantile_returns.values) <= 0)
    print(f"分位数收益单调性违规数: {mono_violations}/{n_quantiles-1} (越低越好)")

    return {
        'rank_ic': data['factor'].corr(data['fwd_return'], method='spearman'),
        'ols_r': r_value, 'ols_p': p_value,
        'quantile_returns': quantile_returns,
        'long_short_spread': quantile_returns.iloc[-1] - quantile_returns.iloc[0]
    }

# 一键运行(用 demo 数据: factors 每列分别作为单独因子做分析)
result_momentum = factor_analysis_viz(
    factor_values=factors['momentum'],
    forward_returns=df['returns'].shift(-1).dropna(),
    factor_name='动量因子'
)
print(f"\n✅ 多空价差: {result_momentum['long_short_spread']:.4%}  (rank IC: {result_momentum['rank_ic']:.3f})")
