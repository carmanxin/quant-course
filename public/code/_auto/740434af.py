# @quantlab/output: 740434af
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
# 注:本案例纯 matplotlib, 不依赖 seaborn(浏览器沙箱不支持)。
from scipy import stats
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker

def quant_dashboard(price_data, strategy_nav=None, benchmark_nav=None,
                    returns=None, drawdowns=None, monthly_returns=None):
    """
    创建专业的量化策略仪表盘，整合多个关键诊断图表
    """
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(20, 14))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35)

    # === 1. 价格走势与交易信号 (占据2列) ===
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(price_data.index, price_data['Close'], linewidth=0.8, color='#2c3e50', label='收盘价')

    # 如果提供了净值曲线
    if strategy_nav is not None:
        ax1_twin = ax1.twinx()
        ax1_twin.plot(strategy_nav.index, strategy_nav.values,
                      linewidth=1.2, color='#e74c3c', alpha=0.8, label='策略净值')
        ax1_twin.set_ylabel('策略净值', color='#e74c3c')
        ax1_twin.legend(loc='upper left')

    ax1.set_title('价格走势与策略表现', fontsize=13, fontweight='bold')
    ax1.set_ylabel('价格')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # === 2. 收益率分布 ===
    ax2 = fig.add_subplot(gs[0, 2])
    if returns is not None:
        returns_clean = returns.dropna()
        ax2.hist(returns_clean, bins=50, density=True, color='steelblue',
                alpha=0.6, edgecolor='white')

        # 叠加正态分布
        x = np.linspace(returns_clean.min(), returns_clean.max(), 200)
        ax2.plot(x, stats.norm.pdf(x, returns_clean.mean(), returns_clean.std()),
                'r-', linewidth=2, label='正态分布')

        ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax2.axvline(x=returns_clean.mean(), color='red', linestyle='--',
                   linewidth=1, label=f'均值={returns_clean.mean():.4f}')

        ax2.set_title('收益率分布', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)

    # === 3. 累计收益对比 ===
    ax3 = fig.add_subplot(gs[1, :2])
    if strategy_nav is not None:
        ax3.plot(strategy_nav.index, strategy_nav.values,
                linewidth=1.5, color='#e74c3c', label='策略')
    if benchmark_nav is not None:
        ax3.plot(benchmark_nav.index, benchmark_nav.values,
                linewidth=1.5, color='#3498db', alpha=0.7, label='基准')

    ax3.set_title('累计净值对比', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=1.0, color='black', linestyle='--', linewidth=0.5)

    # === 4. 回撤曲线 ===
    ax4 = fig.add_subplot(gs[1, 2])
    if drawdowns is not None:
        ax4.fill_between(drawdowns.index, 0, drawdowns.values * 100,
                        color='#e74c3c', alpha=0.5)
        ax4.plot(drawdowns.index, drawdowns.values * 100,
                linewidth=0.5, color='#c0392b')

        max_dd = drawdowns.min() * 100
        max_dd_date = drawdowns.idxmin()
        ax4.axhline(y=max_dd, color='darkred', linestyle='--', linewidth=1,
                   label=f'最大回撤={max_dd:.1f}%')

        ax4.set_title('回撤曲线', fontsize=12, fontweight='bold')
        ax4.set_ylabel('回撤 (%)')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)

    # === 5. 月度收益热力图(纯 matplotlib,无需 seaborn) ===
    ax5 = fig.add_subplot(gs[2, 0])
    if monthly_returns is not None:
        # 构建月度收益矩阵
        if isinstance(monthly_returns, pd.Series):
            monthly_returns = monthly_returns.copy()
        mr = monthly_returns.values if hasattr(monthly_returns, 'values') else monthly_returns
        nrows, ncols = mr.shape
        im5 = ax5.imshow(mr, cmap='RdYlGn', aspect='equal')
        # 写百分比注释
        for i in range(nrows):
            for j in range(ncols):
                v = mr[i, j]
                color = 'white' if abs(v) > 0.05 else 'black'
                ax5.text(j, i, f'{v:.1%}', ha='center', va='center',
                         color=color, fontsize=7)
        # 行/列标签(若是 DataFrame)
        if hasattr(monthly_returns, 'columns'):
            ax5.set_xticks(range(ncols))
            ax5.set_xticklabels(monthly_returns.columns, fontsize=7, rotation=0)
        if hasattr(monthly_returns, 'index'):
            ax5.set_yticks(range(nrows))
            ax5.set_yticklabels(monthly_returns.index, fontsize=7)
        ax5.set_title('月度收益热力图 (%)', fontsize=12, fontweight='bold')

    # === 6. 滚动指标 ===
    ax6 = fig.add_subplot(gs[2, 1])
    if returns is not None:
        window = min(60, len(returns) // 5)
        rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)

        ax6.plot(rolling_sharpe.index, rolling_sharpe.values,
                linewidth=0.8, color='#2ecc71', label=f'滚动夏普 ({window}日)')
        ax6.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax6.set_title('滚动夏普比率', fontsize=12, fontweight='bold')
        ax6.legend(fontsize=8)
        ax6.grid(True, alpha=0.3)

    # === 7. 关键统计指标 ===
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.axis('off')

    if returns is not None:
        returns_clean = returns.dropna()
        stats_text = f"""
        策略统计摘要
        {'─' * 30}
        年化收益率:   {returns_clean.mean()*252:>8.2%}
        年化波动率:   {returns_clean.std()*np.sqrt(252):>8.2%}
        夏普比率:     {(returns_clean.mean()/returns_clean.std())*np.sqrt(252):>8.2f}
        最大回撤:     {drawdowns.min():>8.2%}
        胜率:         {(returns_clean>0).mean():>8.1%}
        盈亏比:       {abs(returns_clean[returns_clean>0].mean()/returns_clean[returns_clean<0].mean()):>8.2f}
        偏度:         {stats.skew(returns_clean):>8.2f}
        超额峰度:     {stats.kurtosis(returns_clean):>8.2f}
        Calmar比率:  {(returns_clean.mean()*252)/abs(drawdowns.min()):>8.2f}
        """

        ax7.text(0.05, 0.95, stats_text, transform=ax7.transAxes,
                fontsize=10, fontfamily='monospace', verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    fig.suptitle('量化策略分析仪表盘', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.show()

    return fig

# 一键运行(用 demo 数据构造完整的策略分析面板)
_np.random.seed(11)
_strategy_rets = pd.Series(df['returns'] * signal[:-1], index=df.index).iloc[1:]
_strategy_nav  = (1 + _strategy_rets).cumprod()
_bench_nav     = (1 + df['returns']).cumprod()
_drawdowns     = _strategy_nav / _strategy_nav.cummax() - 1
_monthly       = _strategy_rets.resample('B').sum().resample('ME').sum().to_frame('ret')
_monthly['year']  = _monthly.index.year
_monthly['month'] = _monthly.index.month
_monthly_pivot = _monthly.pivot(index='year', columns='month', values='ret').fillna(0)

quant_dashboard(
    price_data=df[['Close']],
    strategy_nav=_strategy_nav,
    benchmark_nav=_bench_nav,
    returns=_strategy_rets,
    drawdowns=_drawdowns,
    monthly_returns=_monthly_pivot
)
print(f"\n✅ 仪表盘已生成:价格走势 / 收益分布 / 净值对比 / 回撤 / 月度热图 / 滚动夏普 / 关键统计")
