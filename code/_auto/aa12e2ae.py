# @quantlab/output: aa12e2ae
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 注:本案例纯 matplotlib, 不依赖 seaborn(浏览器沙箱不支持)。

def parameter_sensitivity_heatmap(price_data, short_range, long_range):
    """
    双均线策略的参数敏感性分析
    通过热力图展示不同参数组合下的夏普比率
    """
    returns = price_data.pct_change().dropna()
    sharpe_matrix = np.zeros((len(short_range), len(long_range)))

    for i, short in enumerate(short_range):
        for j, long in enumerate(long_range):
            if short >= long:
                sharpe_matrix[i, j] = np.nan
                continue

            # 计算信号
            ma_short = price_data.rolling(short).mean()
            ma_long = price_data.rolling(long).mean()
            position = (ma_short > ma_long).astype(int).shift(1)

            # 计算策略收益和夏普
            strategy_returns = position * returns
            strategy_returns = strategy_returns.dropna()

            if len(strategy_returns) > 0 and strategy_returns.std() > 0:
                sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
            else:
                sharpe = np.nan
            sharpe_matrix[i, j] = sharpe

    # 绘制热力图(纯 matplotlib, 无需 seaborn)
    plt.figure(figsize=(12, 8))
    masked = np.where(np.isnan(sharpe_matrix), np.nan, sharpe_matrix)
    im = plt.imshow(masked, cmap='RdYlGn', aspect='auto', vmin=-2, vmax=2)
    plt.xticks(range(len(long_range)), long_range)
    plt.yticks(range(len(short_range)), short_range)
    # 在每个 cell 上写数值(skip 不可行情形)
    for i in range(sharpe_matrix.shape[0]):
        for j in range(sharpe_matrix.shape[1]):
            v = sharpe_matrix[i, j]
            if not np.isnan(v):
                color = 'white' if abs(v) > 1.0 else 'black'
                plt.text(j, i, f'{v:.2f}', ha='center', va='center',
                         color=color, fontsize=10)
    cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
    cbar.set_label('夏普比率')
    plt.xlabel('长期均线窗口（天）')
    plt.ylabel('短期均线窗口（天）')
    plt.title('双均线策略参数敏感性热力图\n（孤峰=过拟合迹象，高原=稳健）')
    plt.tight_layout()
    plt.show()

    return sharpe_matrix

# 一键运行(demo 数据已自动注入 df['Close'])
param_sensitivity = parameter_sensitivity_heatmap(
    df['Close'],
    short_range=[5, 10, 15, 20, 25, 30],
    long_range=[40, 50, 60, 80, 100, 120, 150]
)
best_idx = np.unravel_index(np.nanargmax(param_sensitivity), param_sensitivity.shape)
short_vals = [5, 10, 15, 20, 25, 30]
long_vals  = [40, 50, 60, 80, 100, 120, 150]
print('=' * 50)
print(f"✅ 最佳参数: 短期均线={short_vals[best_idx[0]]}, 长期均线={long_vals[best_idx[1]]}")
print(f"✅ 最佳夏普比率: {np.nanmax(param_sensitivity):.3f}")
print(f"⚠️  对比最低夏普: {np.nanmin(param_sensitivity):.3f} (差距越大越可能过拟合)")
