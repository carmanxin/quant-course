# @quantlab/output: 55469491
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
# 注:本案例纯 matplotlib + scipy, 不依赖 seaborn(浏览器沙箱不支持)。

def diagnose_return_distribution(returns, title='收益率分布诊断'):
    """
    全面诊断收益分布的统计特征
    """
    returns = returns.dropna()
    n = len(returns)

    # 基础统计量
    mean = returns.mean()
    std = returns.std()
    skew = stats.skew(returns)
    kurt = stats.kurtosis(returns)  # 超额峰度 (excess kurtosis, normal=0)
    jb_stat, jb_p = stats.jarque_bera(returns)  # Jarque-Bera正态性检验

    # VaR 和 CVaR
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    cvar_95 = returns[returns <= var_95].mean()  # Expected Shortfall

    # 创建诊断图表
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # 1. 收益率时序图
    axes[0, 0].plot(returns.index, returns.values, linewidth=0.5, alpha=0.7)
    axes[0, 0].axhline(y=mean, color='red', linestyle='--', alpha=0.5, label=f'均值={mean:.4f}')
    axes[0, 0].axhline(y=mean + 2*std, color='orange', linestyle=':', alpha=0.5, label=f'±2σ')
    axes[0, 0].axhline(y=mean - 2*std, color='orange', linestyle=':', alpha=0.5)
    axes[0, 0].set_title('收益率时序')
    axes[0, 0].legend(fontsize=8)

    # 2. 直方图 vs 正态分布
    axes[0, 1].hist(returns, bins=50, density=True, alpha=0.6, color='steelblue', edgecolor='white')
    x_range = np.linspace(returns.min(), returns.max(), 200)
    axes[0, 1].plot(x_range, stats.norm.pdf(x_range, mean, std), 'r-', linewidth=2, label='正态分布拟合')
    axes[0, 1].set_title(f'收益率分布\n偏度={skew:.3f}, 超额峰度={kurt:.3f}')
    axes[0, 1].legend(fontsize=8)

    # 3. Q-Q图 (Quantile-Quantile Plot)
    stats.probplot(returns, dist='norm', plot=axes[0, 2])
    axes[0, 2].set_title(f'Q-Q图 (JB p值={jb_p:.4f})')

    # 4. 自相关图
    from statsmodels.graphics.tsaplots import plot_acf
    plot_acf(returns, ax=axes[1, 0], lags=30)
    axes[1, 0].set_title('收益率自相关')

    # 5. 滚动波动率
    rolling_vol = returns.rolling(20).std() * np.sqrt(252)
    axes[1, 1].plot(rolling_vol.index, rolling_vol.values, linewidth=0.8)
    axes[1, 1].set_title('滚动年化波动率 (20日)')

    # 6. 左尾放大（关注极端亏损）
    left_tail = returns[returns < returns.quantile(0.10)]
    axes[1, 2].hist(left_tail, bins=30, density=True, alpha=0.6, color='darkred', edgecolor='white')
    axes[1, 2].axvline(x=var_95, color='orange', linestyle='--', label=f'VaR 95%={var_95:.2%}')
    axes[1, 2].axvline(x=var_99, color='red', linestyle='--', label=f'VaR 99%={var_99:.2%}')
    axes[1, 2].set_title(f'左尾分布\nCVaR 95%={cvar_95:.2%}')
    axes[1, 2].legend(fontsize=8)

    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # 打印统计报告
    print("=" * 50)
    print(f"样本量: {n}")
    print(f"均值: {mean:.6f} (年化: {mean*252:.2%})")
    print(f"标准差: {std:.6f} (年化: {std*np.sqrt(252):.2%})")
    print(f"偏度: {skew:.4f} {'(显著负偏⚠️)' if skew < -0.5 else ''}")
    print(f"超额峰度: {kurt:.4f} {'(厚尾⚠️)' if kurt > 1 else ''}")
    print(f"Jarque-Bera p值: {jb_p:.6f} {'(拒绝正态分布)' if jb_p < 0.05 else '(无法拒绝正态分布)'}")
    print(f"VaR (95%): {var_95:.4%}")
    print(f"VaR (99%): {var_99:.4%}")
    print(f"CVaR (95%): {cvar_95:.4%}")

    return {
        'mean': mean, 'std': std, 'skew': skew, 'kurt': kurt,
        'jb_pvalue': jb_p, 'var_95': var_95, 'var_99': var_99, 'cvar_95': cvar_95
    }

# 一键运行(用 demo 数据 df['returns'] 作为收益率序列)
diagnose_return_distribution(df['returns'].rename('returns'))
