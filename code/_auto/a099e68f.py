# @quantlab/output: a099e68f
import numpy as np
import pandas as pd
from scipy import stats


class NorthboundFactorEngine:
    """北向资金因子引擎"""

    def __init__(self, northbound_flow: pd.DataFrame, prices: pd.DataFrame):
        """
        Parameters
        ----------
        northbound_flow : pd.DataFrame
            北向资金日度持股数据
            columns: ['date', 'code', 'hold_shares', 'hold_pct',
                     'buy_amount', 'sell_amount', 'net_buy_amount']
        prices : pd.DataFrame
            股票价格数据（用于计算市值和收益）
        """
        self.flow = northbound_flow
        self.prices = prices

    def compute_flow_factors(self) -> pd.DataFrame:
        """计算北向资金流因子"""
        df = self.flow.copy()

        # 按股票和日期排序
        df = df.sort_values(['code', 'date'])

        for code in df['code'].unique():
            mask = df['code'] == code
            code_data = df.loc[mask].copy()

            # 因子1: 当日净买入占比（净买入额/当日成交额）
            df.loc[mask, 'net_buy_ratio'] = (
                code_data['net_buy_amount'] / code_data['total_amount'].replace(0, np.nan)
            )

            # 因子2: 持股比例变动（当日持股比例 - 前日持股比例）
            df.loc[mask, 'hold_pct_change'] = code_data['hold_pct'].diff()

            # 因子3: 5日累计净买入占比
            df.loc[mask, 'net_buy_ratio_5d'] = (
                code_data['net_buy_amount'].rolling(5).sum() /
                code_data['total_amount'].rolling(5).sum().replace(0, np.nan)
            )

            # 因子4: 20日持股比例趋势（Z-score法）
            hold_pct_20d = code_data['hold_pct'].rolling(20)
            df.loc[mask, 'hold_pct_trend_20d'] = (
                (code_data['hold_pct'] - hold_pct_20d.mean()) /
                hold_pct_20d.std().replace(0, np.nan)
            )

            # 因子5: 连续净买入天数
            net_buy_sign = (code_data['net_buy_amount'] > 0).astype(int)
            df.loc[mask, 'consecutive_buy_days'] = (
                net_buy_sign.groupby((net_buy_sign != net_buy_sign.shift()).cumsum()).cumcount() + 1
            ) * net_buy_sign

            # 因子6: 北向资金加速度（持股变动的一阶差分）
            df.loc[mask, 'flow_acceleration'] = code_data['hold_pct_change'].diff()

            # 因子7: 净买入的波动率调整
            net_buy_rolling = code_data['net_buy_ratio'].rolling(20)
            df.loc[mask, 'net_buy_vol_adj'] = (
                code_data['net_buy_ratio'] / net_buy_rolling.std().replace(0, np.nan)
            )

        return df

    def compute_holding_concentration(self, sector_mapping: dict = None) -> pd.DataFrame:
        """
        计算北向资金持仓集中度

        高集中度增持的行业/个股可能具有更强的Alpha信号
        """
        df = self.flow.copy()

        # 按日期统计各股票的北向资金持有市值
        if 'market_cap' not in df.columns:
            # 合并价格和持股量计算持仓市值
            df = df.merge(
                self.prices[['date', 'code', 'close']],
                on=['date', 'code'], how='left'
            )
            df['hold_market_value'] = df['hold_shares'] * df['close']

        # 每日北向资金持仓总市值
        daily_total = df.groupby('date')['hold_market_value'].sum().reset_index()
        daily_total.columns = ['date', 'total_hold_mv']
        df = df.merge(daily_total, on='date', how='left')

        # 持仓权重
        df['northbound_weight'] = df['hold_market_value'] / df['total_hold_mv']

        # 权重变化：北向资金的边际配置
        df['weight_change'] = df.groupby('code')['northbound_weight'].diff()

        return df

    def generate_composite_signal(self) -> pd.DataFrame:
        """
        生成北向资金综合信号

        将多个北向因子合成为一个综合评分
        """
        flow_factors = self.compute_flow_factors()
        holding_data = self.compute_holding_concentration()

        merged = flow_factors.merge(
            holding_data[['date', 'code', 'northbound_weight', 'weight_change']],
            on=['date', 'code'], how='left'
        )

        # 因子列表和方向（1=因子值越大越好，-1=因子值越小越好）
        factor_config = {
            'net_buy_ratio': 1,
            'hold_pct_change': 1,
            'net_buy_ratio_5d': 1,
            'hold_pct_trend_20d': 1,
            'consecutive_buy_days': 1,
            'flow_acceleration': 1,
            'net_buy_vol_adj': 1,
            'weight_change': 1
        }

        # 截面标准化
        merged = merged.set_index(['date', 'code'])

        composite = pd.Series(0.0, index=merged.index)
        valid_count = pd.Series(0, index=merged.index)

        for factor, direction in factor_config.items():
            if factor in merged.columns:
                # 截面Z-score
                zscore = merged[factor].groupby('date').transform(
                    lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
                ) * direction

                composite += zscore.fillna(0)
                valid_count += zscore.notna().astype(float)

        # 取平均
        composite = composite / valid_count.replace(0, np.nan)
        composite = composite.reset_index()
        composite.columns = ['date', 'code', 'northbound_signal']

        return composite
