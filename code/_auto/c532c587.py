# @quantlab/output: c532c587
class DragonTigerAnalyzer:
    """龙虎榜数据量化分析器"""

    # 常见机构席位标识（示例）
    INSTITUTION_KEYWORDS = ['机构专用', '深股通专用', '沪股通专用',
                            'QFII', '社保基金']

    def __init__(self, dragon_tiger_data: pd.DataFrame):
        """
        Parameters
        ----------
        dragon_tiger_data : pd.DataFrame
            columns: ['date', 'code', 'name', 'reason',
                     'buy_seat_1', 'buy_amount_1', ..., 'buy_seat_5', 'buy_amount_5',
                     'sell_seat_1', 'sell_amount_1', ..., 'sell_seat_5', 'sell_amount_5',
                     'total_buy', 'total_sell']
        """
        self.data = dragon_tiger_data

    def classify_seats(self) -> pd.DataFrame:
        """对龙虎榜席位进行分类"""
        df = self.data.copy()

        def is_institution(seat_name: str) -> bool:
            if pd.isna(seat_name):
                return False
            return any(kw in str(seat_name) for kw in self.INSTITUTION_KEYWORDS)

        # 统计机构买入/卖出金额
        inst_buy_cols = []
        inst_sell_cols = []

        for i in range(1, 6):
            buy_seat = f'buy_seat_{i}'
            buy_amount = f'buy_amount_{i}'
            sell_seat = f'sell_seat_{i}'
            sell_amount = f'sell_amount_{i}'

            if buy_seat in df.columns:
                df[f'inst_buy_{i}'] = df[buy_seat].apply(
                    lambda x: df.loc[df[buy_seat] == x, buy_amount].iloc[0]
                    if is_institution(x) else 0
                ) if False else np.where(
                    df[buy_seat].apply(is_institution), df[buy_amount], 0
                )

            if sell_seat in df.columns:
                df[f'inst_sell_{i}'] = np.where(
                    df[sell_seat].apply(is_institution), df[sell_amount], 0
                )

        # 汇总机构净买入
        if 'total_buy' in df.columns:
            df['inst_total_buy'] = df[[f'inst_buy_{i}' for i in range(1, 6)
                                        if f'inst_buy_{i}' in df.columns]].sum(axis=1)
            df['inst_total_sell'] = df[[f'inst_sell_{i}' for i in range(1, 6)
                                         if f'inst_sell_{i}' in df.columns]].sum(axis=1)
            df['inst_net_buy'] = df['inst_total_buy'] - df['inst_total_sell']
            df['inst_buy_ratio'] = df['inst_total_buy'] / df['total_buy'].replace(0, np.nan)
            df['inst_sell_ratio'] = df['inst_total_sell'] / df['total_sell'].replace(0, np.nan)

        return df

    def seat_following_signal(self) -> pd.DataFrame:
        """
        席位跟踪信号

        识别具有持续盈利能力的"实力席位"，跟踪其操作方向
        """
        classified = self.classify_seats()

        # 计算历史上这五个席位的后续收益表现
        seat_performance = {}

        for i in range(1, 6):
            buy_seat_col = f'buy_seat_{i}'
            if buy_seat_col not in classified.columns:
                continue

            for seat in classified[buy_seat_col].dropna().unique():
                trades = classified[classified[buy_seat_col] == seat]
                if len(trades) < 10:
                    continue

                # 假设持有1天的收益
                avg_1d_return = trades.get('next_day_return', pd.Series(0)).mean()
                win_rate = (trades.get('next_day_return', pd.Series(0)) > 0).mean()

                seat_performance[seat] = {
                    'n_trades': len(trades),
                    'avg_1d_return': avg_1d_return,
                    'win_rate': win_rate,
                    'score': avg_1d_return * win_rate  # 综合评分
                }

        # 筛选实力席位（前20%）
        if seat_performance:
            perf_df = pd.DataFrame(seat_performance).T
            elite_seats = perf_df[perf_df['score'] > perf_df['score'].quantile(0.8)].index

            # 生成跟随信号：实力席位净买入 > 0
            classified['elite_seat_signal'] = classified.apply(
                lambda row: self._check_elite_seats(row, elite_seats), axis=1
            )

        return classified

    def _check_elite_seats(self, row, elite_seats) -> int:
        """检查某日的龙虎榜是否有实力席位参与"""
        for i in range(1, 6):
            if row.get(f'buy_seat_{i}') in elite_seats:
                if row.get(f'buy_amount_{i}', 0) > row.get(f'sell_amount_{i}', 0):
                    return 1
        return 0

    def list_reason_analysis(self) -> pd.DataFrame:
        """按上榜原因分析后续表现"""
        df = self.data.copy()

        if 'reason' not in df.columns or 'next_day_return' not in df.columns:
            return pd.DataFrame()

        reason_stats = df.groupby('reason').agg(
            n_events=('next_day_return', 'count'),
            avg_next_day_return=('next_day_return', 'mean'),
            win_rate=('next_day_return', lambda x: (x > 0).mean()),
            avg_inst_net_buy=('inst_net_buy', 'mean')
        ).sort_values('avg_next_day_return', ascending=False)

        return reason_stats
