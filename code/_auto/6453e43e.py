# @quantlab/output: 6453e43e
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


class StrategyMVP:
    """策略快速验证框架"""

    def __init__(self, prices: pd.DataFrame):
        """
        Parameters
        ----------
        prices : pd.DataFrame
            股票价格矩阵，index为日期，columns为股票代码
        """
        self.prices = prices
        self.returns = prices.pct_change()

    def compute_signal(self, window: int = 20) -> pd.DataFrame:
        """计算待验证的信号（示例：动量反转）"""
        # 替换为你的策略信号逻辑
        signal = -self.returns.rolling(window).mean()  # 短期反转
        return signal

    def group_analysis(self, signal: pd.DataFrame, n_groups: int = 5):
        """分组分析：将股票按信号分为N组，计算各组收益"""
        returns = self.returns.shift(-1)  # 下一期收益

        results = []
        for date in signal.index:
            sig_t = signal.loc[date].dropna()
            if len(sig_t) < n_groups * 5:
                continue

            labels = pd.qcut(sig_t, n_groups, labels=False)
            for g in range(n_groups):
                mask = labels == g
                ret = returns.loc[date, mask].mean()
                results.append({
                    'date': date,
                    'group': g + 1,
                    'return': ret
                })

        df = pd.DataFrame(results)

        # 计算各组累计收益
        cum_ret = df.pivot(index='date', columns='group', values='return').cumsum()

        # 顶部组与底部组的对冲收益
        spread = cum_ret.iloc[:, -1] - cum_ret.iloc[:, 0]

        return cum_ret, spread

    def quick_evaluation(self, spread: pd.Series) -> dict:
        """快速评估对冲组合的表现"""
        ann_return = spread.mean() * 252
        ann_vol = spread.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0

        # 胜率
        win_rate = (spread > 0).mean()

        # 最大回撤
        cum = spread.cumsum()
        running_max = cum.cummax()
        drawdown = cum - running_max
        max_dd = drawdown.min()

        return {
            'annual_return': f'{ann_return:.4f}',
            'annual_volatility': f'{ann_vol:.4f}',
            'sharpe_ratio': f'{sharpe:.2f}',
            'win_rate': f'{win_rate:.2%}',
            'max_drawdown': f'{max_dd:.4f}'
        }


# 使用示例
if __name__ == '__main__':
    # 生成模拟数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='B')
    stocks = [f'STOCK_{i:03d}' for i in range(100)]

    prices = pd.DataFrame(
        np.random.randn(len(dates), len(stocks)).cumsum(axis=0) * 0.02 + 10,
        index=dates, columns=stocks
    )

    mvp = StrategyMVP(prices)
    signal = mvp.compute_signal(window=20)
    cum_ret, spread = mvp.group_analysis(signal, n_groups=5)
    results = mvp.quick_evaluation(spread)

    print("===== MVP 快速验证结果 =====")
    for k, v in results.items():
        print(f"{k}: {v}")
