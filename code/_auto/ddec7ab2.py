# @quantlab/output: ddec7ab2
import numpy as np
import pandas as pd

def calculate_all_metrics(equity_curve, benchmark=None, rf_rate=0.03):
    """
    计算全套绩效指标

    Parameters:
        equity_curve: pd.Series, 净值曲线（index为日期）
        benchmark: pd.Series, 基准净值曲线
        rf_rate: 无风险利率（年化）
    """
    # 日收益率
    returns = equity_curve.pct_change().dropna()
    n_days = len(returns)
    years = n_days / 252

    # === 收益指标 ===
    total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1
    annual_return = (1 + total_return) ** (1 / years) - 1

    # === 风险指标 ===
    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252)

    # 最大回撤
    rolling_max = equity_curve.expanding().max()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # 下行波动率
    downside_returns = returns[returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(252)

    # === 风险调整收益 ===
    sharpe = (annual_return - rf_rate) / annual_vol if annual_vol > 0 else 0
    sortino = (annual_return - rf_rate) / downside_vol if downside_vol > 0 else 0
    calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

    # 信息比率（相对于基准）
    if benchmark is not None:
        excess = returns - benchmark.pct_change().dropna()
        tracking_error = excess.std() * np.sqrt(252)
        excess_return = annual_return - calculate_annual_return(benchmark)
        ir = excess_return / tracking_error if tracking_error > 0 else 0
    else:
        ir = np.nan

    # === 稳定性指标 ===
    win_rate = (returns > 0).mean()
    win_mean = returns[returns > 0].mean()
    lose_mean = returns[returns < 0].mean()
    profit_loss_ratio = abs(win_mean / lose_mean) if lose_mean != 0 else np.inf

    # 最长回撤恢复时间
    max_dd_end = drawdown.idxmin()
    max_dd_start = drawdown.loc[:max_dd_end].idxmax()

    # Calmar Ratios per rolling year
    rolling_1y = returns.rolling(252).mean() * 252  # rolling annual return
    rolling_vol = returns.rolling(252).std() * np.sqrt(252)

    metrics = {
        '累计收益率': f'{total_return:.2%}',
        '年化收益率': f'{annual_return:.2%}',
        '年化波动率': f'{annual_vol:.2%}',
        '最大回撤': f'{max_drawdown:.2%}',
        '下行波动率': f'{downside_vol:.2%}',
        '夏普比率': f'{sharpe:.2f}',
        '索提诺比率': f'{sortino:.2f}',
        '卡玛比率': f'{calmar:.2f}',
        '信息比率': f'{ir:.2f}',
        '胜率': f'{win_rate:.2%}',
        '盈亏比': f'{profit_loss_ratio:.2f}',
        '最大回撤发生时间': str(max_dd_end),
    }

    return pd.Series(metrics)
