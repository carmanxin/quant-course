# @quantlab/output: 51a325f6
import numpy as np
import pandas as pd

class LimitBoardTimeSeriesAnalysis:
    """涨跌停板时间序列分析"""

    def __init__(self, daily_data: pd.DataFrame):
        self.daily = daily_data

    def daily_limit_up_ratio(self) -> pd.Series:
        """每日涨停股票占比"""
        limit_up_counts = self.daily[self.daily['is_limit_up']].groupby('date').size()
        total_counts = self.daily.groupby('date').size()
        return (limit_up_counts / total_counts).fillna(0)

    def limit_up_concentration(self) -> pd.Series:
        """
        涨停板集中度指数：涨停股票集中在少数行业还是分散在各行业

        高集中度通常对应主题驱动行情，低集中度对应普涨行情
        """
        limit_up_stocks = self.daily[self.daily['is_limit_up']]

        # 使用赫芬达尔指数（HHI）衡量行业集中度
        hhi = limit_up_stocks.groupby(['date', 'sector']).size() \
                             .groupby('date').apply(
            lambda x: ((x / x.sum()) ** 2).sum()
        )
        return hhi

    def limit_board_market_sentiment(self) -> pd.DataFrame:
        """
        涨跌停板市场情绪指标

        计算涨停数、跌停数、涨跌停比，作为市场情绪的量化代理
        """
        daily_stats = pd.DataFrame()
        daily_stats['limit_up_count'] = self.daily[self.daily['is_limit_up']].groupby('date').size()
        daily_stats['limit_down_count'] = self.daily[self.daily['is_limit_down']].groupby('date').size()

        daily_stats['up_down_ratio'] = daily_stats['limit_up_count'] / \
                                        daily_stats['limit_down_count'].replace(0, np.nan)

        # 情绪指标Z-score
        daily_stats['sentiment_z'] = (daily_stats['up_down_ratio'] -
                                       daily_stats['up_down_ratio'].rolling(60).mean()) / \
                                      daily_stats['up_down_ratio'].rolling(60).std()

        return daily_stats

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(103)
_rows = []
for _i in range(40):
    _d = f'2024-04-{_i+1:02d}'
    for _c in ['600001', '600002', '000003', '000004', '300001']:
        _up = 1 if np.random.rand() < 0.08 else 0
        _down = 1 if np.random.rand() < 0.05 else 0
        _rows.append({'date': _d, 'code': _c, 'is_limit_up': _up, 'is_limit_down': _down,
                      'close': 10 + _i * 0.1, 'pre_close': 10 + (_i - 1) * 0.1})
_daily_data = pd.DataFrame(_rows)
_ts = LimitBoardTimeSeriesAnalysis(daily_data)
try:
    print('每日涨停比例:', _ts.daily_limit_up_ratio().tail(3))
except Exception:
    pass
try:
    print('涨停集中度:', _ts.limit_up_concentration())
except Exception:
    pass
try:
    print('市场情绪:', _ts.limit_board_market_sentiment())
except Exception:
    pass
