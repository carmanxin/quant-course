# @quantlab/output: bd0625e6
class SubNewStockStrategy:
    """次新股策略"""

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def time_since_ipo(self) -> pd.Series:
        """计算上市以来天数"""
        return (self.data['date'] - self.data['ipo_date']).dt.days

    def lockup_expiry_effect(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        限售股解禁效应分析

        返回解禁日前后的平均超额收益模式
        """
        # 计算每日相对基准的超额收益
        stock_data['excess_return'] = stock_data['return'] - stock_data['market_return']

        # 以解禁日为中心window窗口的累计超额收益
        window = 60
        results = []

        for expiry_date in stock_data['lockup_expiry_date'].unique():
            idx = stock_data['date'].searchsorted(expiry_date)
            start = max(0, idx - window)
            end = min(len(stock_data), idx + window)

            if end - start < window:
                continue

            segment = stock_data.iloc[start:end].copy()
            segment['event_day'] = range(-window, window)[:len(segment)]
            results.append(segment[['event_day', 'excess_return']])

        if not results:
            return pd.DataFrame()

        all_events = pd.concat(results)
        avg_effect = all_events.groupby('event_day')['excess_return'].mean().cumsum()

        return avg_effect.reset_index()

    def sub_new_stock_signal(self, min_listed_days: int = 30,
                              max_listed_days: int = 180) -> pd.DataFrame:
        """生成次新股交易信号"""
        df = self.data.copy()
        df['days_listed'] = self.time_since_ipo()

        # 筛选次新股
        mask = (df['days_listed'] >= min_listed_days) & \
               (df['days_listed'] <= max_listed_days)

        sub_new = df[mask].copy()

        # 动量因子：上市以来的累计超额收益
        sub_new['cum_excess_since_ipo'] = sub_new.groupby('code')['excess_return'].cumsum()

        # 成交量因子：近期成交量相对前期变化
        sub_new['vol_ratio'] = (
            sub_new.groupby('code')['volume'].transform(lambda x: x.rolling(10).mean()) /
            sub_new.groupby('code')['volume'].transform(lambda x: x.rolling(60).mean())
        )

        # 综合信号
        sub_new['momentum_score'] = sub_new['cum_excess_since_ipo'].rolling(20).mean().rank(pct=True)
        sub_new['volume_score'] = sub_new['vol_ratio'].rank(pct=True)

        sub_new['composite_signal'] = 0.6 * sub_new['momentum_score'] + \
                                       0.4 * sub_new['volume_score']

        return sub_new.sort_values('composite_signal', ascending=False)
