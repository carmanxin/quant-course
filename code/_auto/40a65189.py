# @quantlab/output: 40a65189
import numpy as np
import pandas as pd


class LimitUpSignalGenerator:
    """涨停板信号生成器"""

    def __init__(self, tick_data: pd.DataFrame, daily_data: pd.DataFrame):
        """
        Parameters
        ----------
        tick_data : pd.DataFrame
            tick级别数据，含买卖盘口
        daily_data : pd.DataFrame
            日频数据，含开盘价、收盘价、成交量等
        """
        self.tick_data = tick_data
        self.daily_data = daily_data

    def identify_limit_up_events(self, limit_pct: float = 0.10) -> pd.DataFrame:
        """识别涨停事件"""
        daily = self.daily_data.copy()

        # 计算涨停价格
        daily['limit_up_price'] = (daily['pre_close'] * (1 + limit_pct)).round(2)
        daily['limit_down_price'] = (daily['pre_close'] * (1 - limit_pct)).round(2)

        # 识别涨停日：收盘价 == 涨停价且成交量 > 0
        daily['is_limit_up'] = (daily['close'] >= daily['limit_up_price'] - 0.001) & \
                                (daily['volume'] > 0)

        return daily[['is_limit_up', 'limit_up_price']]

    def compute_seal_strength(self, stock_code: str, date: str) -> dict:
        """计算封板强度指标"""
        ticks = self.tick_data[
            (self.tick_data['code'] == stock_code) &
            (self.tick_data['date'] == date)
        ].copy()

        if len(ticks) == 0:
            return {}

        # 找到封板区间（价格 == 涨停价 的 tick）
        limit_up_price = self.daily_data.loc[
            (self.daily_data['code'] == stock_code) &
            (self.daily_data['date'] == date), 'limit_up_price'
        ].iloc[0]

        sealed_ticks = ticks[abs(ticks['price'] - limit_up_price) < 0.01]

        if len(sealed_ticks) == 0:
            return {'is_sealed': False}

        # 封板开始时间
        seal_start = sealed_ticks['time'].min()
        seal_duration = sealed_ticks['time'].max() - sealed_ticks['time'].min()

        # 封单量（买一挂单量）
        avg_bid_volume = sealed_ticks['bid_volume_1'].mean()

        # 累计成交量
        total_volume = ticks['volume'].sum()

        # 封成比
        seal_volume_ratio = avg_bid_volume / total_volume if total_volume > 0 else 0

        # 撤单分析：比较挂单量的变化
        bid_changes = sealed_ticks['bid_volume_1'].diff()
        cancellations = abs(bid_changes[bid_changes < 0].sum())
        total_bid = sealed_ticks['bid_volume_1'].sum()
        cancel_rate = cancellations / (total_bid + cancellations) if (total_bid + cancellations) > 0 else 0

        # 开板检测：价格曾离开涨停价又回来
        seal_breaches = 0
        prev_sealed = False
        for _, row in ticks.iterrows():
            is_at_limit = abs(row['price'] - limit_up_price) < 0.01
            if prev_sealed and not is_at_limit:
                seal_breaches += 1
            prev_sealed = is_at_limit

        return {
            'is_sealed': True,
            'seal_start_time': seal_start,
            'seal_duration': seal_duration,
            'seal_volume_ratio': seal_volume_ratio,
            'cancel_rate': cancel_rate,
            'seal_breaches': seal_breaches,
            'avg_bid_volume': avg_bid_volume
        }

    def generate_signal(self, stock_code: str, date: str) -> dict:
        """生成涨停板交易信号"""
        strength = self.compute_seal_strength(stock_code, date)

        if not strength.get('is_sealed'):
            return {'action': 'NONE', 'reason': '未涨停'}

        score = 0

        # 封成比评分（0-40分）
        if strength['seal_volume_ratio'] > 2.0:
            score += 40
        elif strength['seal_volume_ratio'] > 1.0:
            score += 30
        elif strength['seal_volume_ratio'] > 0.5:
            score += 15

        # 撤单率评分（0-25分）
        if strength['cancel_rate'] < 0.10:
            score += 25
        elif strength['cancel_rate'] < 0.20:
            score += 15
        elif strength['cancel_rate'] < 0.30:
            score += 5

        # 开板次数评分（0-20分）
        if strength['seal_breaches'] == 0:
            score += 20
        elif strength['seal_breaches'] == 1:
            score += 10

        # 封板时间评分（0-15分，越早越好）
        seal_hour = strength['seal_start_time'].hour
        if seal_hour < 10:
            score += 15
        elif seal_hour < 11:
            score += 10
        elif seal_hour < 14:
            score += 5

        # 决策
        if score >= 70:
            action = 'BUY'
            confidence = 'HIGH'
        elif score >= 50:
            action = 'BUY'
            confidence = 'MEDIUM'
        else:
            action = 'NONE'
            confidence = 'LOW'

        return {
            'action': action,
            'confidence': confidence,
            'score': score,
            'strength_metrics': strength,
            'expected_next_day_return': self._estimate_next_day_return(score)
        }

    def _estimate_next_day_return(self, score: float) -> float:
        """
        估计次日溢价。基于历史数据拟合评分到次日收益的映射。
        此处使用简化的经验公式。
        """
        if score >= 70:
            return 0.025  # 2.5% 预期次日收益
        elif score >= 50:
            return 0.012
        else:
            return -0.005
