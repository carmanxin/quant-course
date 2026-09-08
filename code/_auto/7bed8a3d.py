# @quantlab/output: 7bed8a3d
import pandas as pd
import numpy as np

class EarningsAnnouncementStrategy:
    """
    盈利公告后漂移（PEAD）策略
    """
    def __init__(self, sue_threshold=1.0, hold_days=30):
        self.sue_threshold = sue_threshold
        self.hold_days = hold_days

    def compute_sue(self, actual_eps, consensus_eps, historical_surprise_std):
        """
        计算标准化意外盈利 (SUE)

        Parameters:
            actual_eps: 实际EPS
            consensus_eps: 分析师一致预期EPS
            historical_surprise_std: 历史EPS惊喜的标准差（滚动8个季度）
        """
        surprise = actual_eps - consensus_eps
        sue = surprise / historical_surprise_std
        return sue

    def generate_signals(self, earnings_calendar, earnings_data, price_data):
        """
        基于盈利公告生成交易信号

        Parameters:
            earnings_calendar: 盈利公告日历
            earnings_data: EPS实际值、预期值等
            price_data: 股价数据
        """
        signals = pd.Series(0, index=price_data.index)

        for date, announcements in earnings_calendar.groupby('announce_date'):
            for _, ann in announcements.iterrows():
                stock = ann['stock_code']
                actual_eps = ann['eps_actual']
                consensus_eps = ann['eps_consensus']
                surprise_std = ann['historical_surprise_std']

                # 计算SUE
                sue = self.compute_sue(actual_eps, consensus_eps, surprise_std)

                # 信号：正惊喜做多，负惊喜做空
                if sue > self.sue_threshold:
                    # 持有self.hold_days天或直到下一期公告
                    end_idx = min(date + pd.Timedelta(days=self.hold_days),
                                  price_data.index[-1])
                    signals.loc[date:end_idx, stock] = 1

                elif sue < -self.sue_threshold:
                    end_idx = min(date + pd.Timedelta(days=self.hold_days),
                                  price_data.index[-1])
                    signals.loc[date:end_idx, stock] = -1

        return signals

    def backtest_pead(self, rank_sue_quantile, returns, forward_period=21):
        """
        基于SUE排名的分位数回测

        将股票按SUE分成5组，做多最高SUE组，做空最低SUE组
        """
        quintile = pd.qcut(rank_sue_quantile, q=5, labels=False)

        long_portfolio = returns[quintile == 4].mean(axis=1)  # 最高SUE组
        short_portfolio = returns[quintile == 0].mean(axis=1)  # 最低SUE组

        long_short = long_portfolio - short_portfolio

        sharpe = long_short.mean() / long_short.std() * np.sqrt(252)
        print(f"PEAD 多空组合 夏普比率: {sharpe:.2f}")

        return long_portfolio, short_portfolio, long_short
