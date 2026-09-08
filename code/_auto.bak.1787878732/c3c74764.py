# @quantlab/output: c3c74764
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller
from scipy import stats
import matplotlib.pyplot as plt

def pair_trading_analysis(price1, price2, name1='Stock1', name2='Stock2',
                          formation_period=252, trading_period=None):
    """
    完整的配对交易分析：从协整检验到交易信号
    """
    # 确保是对数价格
    log_p1 = np.log(price1)
    log_p2 = np.log(price2)

    if trading_period is None:
        trading_period = len(log_p1) - formation_period

    # === 形成期：估计对冲比率和参数 ===
    log_p1_form = log_p1[:formation_period]
    log_p2_form = log_p2[:formation_period]

    # OLS回归得到对冲比率
    X = np.column_stack([np.ones(len(log_p2_form)), log_p2_form])
    beta = np.linalg.lstsq(X, log_p1_form, rcond=None)[0]
    alpha, hedge_ratio = beta[0], beta[1]

    # 计算价差
    spread = log_p1 - (alpha + hedge_ratio * log_p2)
    spread_form = spread[:formation_period]
    spread_trade = spread[formation_period:formation_period + trading_period]

    # 检验残差平稳性
    adf_stat, adf_p, _, _, _ = adfuller(spread_form)
    coint_t, coint_p, _ = coint(log_p1_form, log_p2_form)

    # 计算开仓阈值
    spread_mean = spread_form.mean()
    spread_std = spread_form.std()
    zscore = (spread_trade - spread_mean) / spread_std

    # === 交易期：生成信号 ===
    entry_z = 2.0  # 开仓阈值
    exit_z = 0.5   # 平仓阈值

    position = np.zeros(len(zscore))
    for t in range(1, len(zscore)):
        if position[t-1] == 0:
            if zscore[t] > entry_z:
                position[t] = -1  # 做空价差
            elif zscore[t] < -entry_z:
                position[t] = 1   # 做多价差
            else:
                position[t] = 0
        else:
            if abs(zscore[t]) < exit_z:
                position[t] = 0  # 平仓
            else:
                position[t] = position[t-1]

    # 计算策略收益
    spread_returns = np.diff(spread_trade, prepend=spread_trade[0])
    strategy_returns = position[:-1] * spread_returns[1:]  # 滞后一日

    # 绩效统计
    cum_returns = (1 + pd.Series(strategy_returns)).cumprod()
    annual_ret = np.mean(strategy_returns) * 252
    annual_vol = np.std(strategy_returns) * np.sqrt(252)
    sharpe = annual_ret / annual_vol if annual_vol > 0 else 0

    # 可视化
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    # 价格走势
    axes[0].plot(price1.index[formation_period:],
                 price1.values[formation_period:formation_period+trading_period] / price1.values[formation_period],
                 label=name1, alpha=0.7)
    axes[0].plot(price2.index[formation_period:],
                 price2.values[formation_period:formation_period+trading_period] / price2.values[formation_period],
                 label=name2, alpha=0.7)
    axes[0].axvline(x=price1.index[formation_period], color='red', linestyle='--', alpha=0.5, label='交易开始')
    axes[0].set_title('标准化价格走势')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Z-score和交易信号
    trade_dates = price1.index[formation_period:formation_period + len(zscore)]
    axes[1].plot(trade_dates, zscore, label='Z-score', linewidth=0.8)
    axes[1].axhline(y=entry_z, color='red', linestyle='--', alpha=0.5, label=f'开仓阈值 ±{entry_z}')
    axes[1].axhline(y=-entry_z, color='red', linestyle='--', alpha=0.5)
    axes[1].axhline(y=exit_z, color='green', linestyle=':', alpha=0.5, label=f'平仓阈值 ±{exit_z}')
    axes[1].axhline(y=-exit_z, color='green', linestyle=':', alpha=0.5)
    axes[1].axhline(y=0, color='gray', alpha=0.3)
    axes[1].fill_between(trade_dates, 0, position * max(abs(zscore)),
                         where=(position > 0), color='green', alpha=0.3, label='多头')
    axes[1].fill_between(trade_dates, 0, position * max(abs(zscore)),
                         where=(position < 0), color='red', alpha=0.3, label='空头')
    axes[1].set_title(f'Z-score 和交易信号 (对冲比率={hedge_ratio:.3f})')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # 累计收益
    axes[2].plot(trade_dates, cum_returns, label=f'配对交易 (夏普={sharpe:.2f})', linewidth=0.8)
    axes[2].set_title('累计收益')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print("=" * 50)
    print(f"配对交易分析: {name1} vs {name2}")
    print("=" * 50)
    print(f"对冲比率: {hedge_ratio:.4f}")
    print(f"常数项(Alpha): {alpha:.4f}")
    print(f"ADF检验 (价差平稳性): p={adf_p:.4f} {'✅协整' if adf_p < 0.05 else '❌不协整'}")
    print(f"协整检验: p={coint_p:.4f}")
    print(f"\n交易统计:")
    print(f"  交易次数: {np.sum(np.abs(np.diff(np.insert(position, 0, 0)))) // 2}")
    print(f"  年化收益率: {annual_ret:.2%}")
    print(f"  年化波动率: {annual_vol:.2%}")
    print(f"  夏普比率: {sharpe:.2f}")

    return {
        'hedge_ratio': hedge_ratio, 'alpha': alpha,
        'adf_pvalue': adf_p, 'coint_pvalue': coint_p,
        'sharpe': sharpe, 'spread': spread_trade, 'zscore': zscore,
        'position': position, 'strategy_returns': strategy_returns
    }
