# @quantlab/output: 3fee0615
import numpy as np
import pandas as pd
from scipy import stats


class SectorRotationStrategy:
    """A股行业轮动策略"""

    # 申万一级行业分类（示例）
    SW_SECTORS = [
        '农林牧渔', '采掘', '化工', '钢铁', '有色金属',
        '电子', '家用电器', '食品饮料', '纺织服装', '轻工制造',
        '医药生物', '公用事业', '交通运输', '房地产', '商业贸易',
        '休闲服务', '综合', '建筑材料', '建筑装饰', '电气设备',
        '国防军工', '计算机', '传媒', '通信', '银行',
        '非银金融', '汽车', '机械设备'
    ]

    def __init__(self, sector_returns: pd.DataFrame,
                 sector_valuations: pd.DataFrame = None):
        """
        Parameters
        ----------
        sector_returns : pd.DataFrame
            行业日收益率，index=日期，columns=行业
        sector_valuations : pd.DataFrame
            行业估值数据（PE/PB），index=日期，columns=行业
        """
        self.returns = sector_returns
        self.valuations = sector_valuations

    def compute_momentum_signal(self, lookback: int = 60,
                                 skip: int = 5) -> pd.DataFrame:
        """
        计算动量信号

        Parameters
        ----------
        lookback : int
            回溯窗口（交易日）
        skip : int
            跳过最近N天（避免短期反转效应）
        """
        momentum = self.returns.rolling(lookback).apply(
            lambda x: (1 + x[:-skip]).prod() - 1 if len(x) >= lookback else np.nan
        )
        return momentum

    def compute_value_signal(self) -> pd.DataFrame:
        """
        计算估值信号（估值分位数越低，信号越强）
        """
        if self.valuations is None:
            return None

        # 滚动估值分位数（5年窗口）
        value_percentile = self.valuations.rolling(252 * 5).apply(
            lambda x: stats.percentileofscore(x, x.iloc[-1]) / 100
            if len(x) >= 252 * 3 else np.nan
        )

        # 信号反转：低分位数 -> 高信号
        value_signal = 1 - value_percentile
        return value_signal

    def compute_crowding_indicator(self, window: int = 20) -> pd.DataFrame:
        """
        计算拥挤度指标

        拥挤度高意味着该行业交易过热，前期收益可能来自追涨资金的集中涌入，
        而非基本面的支撑，后续反转风险较大。
        """
        # 成交量拥挤度
        if 'volume' not in self.returns.columns.name.lower():
            # 如果没有成交量数据，用收益率的波动率变化作为代理
            vol = self.returns.rolling(window).std()
            vol_ma = vol.rolling(252).mean()
            vol_ratio = vol / vol_ma  # 当前波动率/历史波动率

            # 高波动率时期通常伴随拥挤交易
            crowding = vol_ratio
        else:
            # 使用成交量指标
            pass

        return crowding

    def compute_composite_signal(self, momentum_weight: float = 0.6,
                                   value_weight: float = 0.3,
                                   crowding_weight: float = 0.1) -> pd.DataFrame:
        """计算综合轮动信号"""
        # 动量信号
        mom_signal = self.compute_momentum_signal(lookback=60)

        # Z-score标准化
        mom_z = mom_signal.sub(mom_signal.mean(axis=1), axis=0)\
                         .div(mom_signal.std(axis=1), axis=0)

        composite = mom_z * momentum_weight

        # 估值信号
        if self.valuations is not None:
            val_signal = self.compute_value_signal()
            val_z = val_signal.sub(val_signal.mean(axis=1), axis=0)\
                             .div(val_signal.std(axis=1), axis=0)
            composite += val_z * value_weight

        # 拥挤度惩罚
        crowding = self.compute_crowding_indicator()
        crowd_z = crowding.sub(crowding.mean(axis=1), axis=0)\
                          .div(crowding.std(axis=1), axis=0)
        composite -= crowd_z * crowding_weight  # 高拥挤度惩罚

        return composite

    def generate_allocation(self, signal: pd.Series,
                            n_select: int = 5,
                            equal_weight: bool = True) -> pd.Series:
        """
        根据信号生成行业配置权重

        Parameters
        ----------
        signal : pd.Series
            某日的行业信号值
        n_select : int
            选出的行业数量
        equal_weight : bool
            True=等权，False=信号加权
        """
        # 选出信号最强的n个行业
        top_sectors = signal.dropna().nlargest(n_select)

        if equal_weight:
            weights = pd.Series(1.0 / n_select, index=top_sectors.index)
        else:
            # 信号归一化为权重
            positive_signals = top_sectors.clip(lower=0)
            if positive_signals.sum() > 0:
                weights = positive_signals / positive_signals.sum()
            else:
                weights = pd.Series(1.0 / n_select, index=top_sectors.index)

        return weights

    def backtest_rotation(self, start_date: str, end_date: str,
                           n_select: int = 5, rebalance_freq: str = 'M') -> pd.DataFrame:
        """行业轮动策略回测"""
        signals = self.compute_composite_signal()

        # 生成再平衡日期
        all_dates = self.returns.loc[start_date:end_date].index

        if rebalance_freq == 'M':
            rebalance_dates = pd.Series(all_dates).dt.to_period('M').drop_duplicates()
            rebalance_dates = all_dates[all_dates.isin(
                all_dates.groupby(all_dates.to_period('M')).apply(lambda x: x[-1])
            )]
        elif rebalance_freq == 'W':
            rebalance_dates = all_dates[::5]  # 约每周
        else:
            rebalance_dates = all_dates

        results = []
        current_weights = None

        for date in all_dates:
            if date in rebalance_dates:
                signal_t = signals.loc[date]
                current_weights = self.generate_allocation(signal_t, n_select=n_select)

            if current_weights is not None and len(current_weights) > 0:
                daily_ret = self.returns.loc[date, current_weights.index]
                portfolio_ret = (daily_ret * current_weights).sum()
            else:
                portfolio_ret = 0

            results.append({
                'date': date,
                'return': portfolio_ret,
                'n_stocks': len(current_weights) if current_weights is not None else 0
            })

        result_df = pd.DataFrame(results).set_index('date')
        result_df['cum_return'] = (1 + result_df['return']).cumprod()

        return result_df


# 行业ETF轮动（实战简化版）
class SectorETFRotation:
    """行业ETF轮动策略"""

    # 代表性行业ETF（示例映射）
    ETF_MAPPING = {
        '银行': '512800',
        '证券': '512880',
        '医药': '512010',
        '消费': '159928',
        '科技': '515000',
        '新能源': '516160',
        '军工': '512660',
        '半导体': '512480',
        '白酒': '512690',
        '房地产': '512200',
    }

    def __init__(self, etf_data: pd.DataFrame, risk_free_rate: float = 0.02):
        self.data = etf_data
        self.rf = risk_free_rate

    def dual_momentum_signal(self, lookback_short: int = 20,
                              lookback_long: int = 60) -> pd.Series:
        """
        双动量信号

        逻辑：短期动量和长期动量的平均值，同时过滤绝对动量为负的ETF
        """
        returns = self.data.pct_change()

        mom_short = returns.rolling(lookback_short).apply(
            lambda x: (1 + x).prod() - 1
        )
        mom_long = returns.rolling(lookback_long).apply(
            lambda x: (1 + x).prod() - 1
        )

        # 绝对动量过滤：长期动量为负的ETF不参与
        mom_filter = mom_long > 0

        # 综合动量 = (短期 + 长期) / 2
        composite = (mom_short + mom_long) / 2
        composite = composite.where(mom_filter)

        return composite.iloc[-1]  # 返回最新一期的信号

    def select_top_etfs(self, signal: pd.Series, n: int = 3) -> list:
        """选择信号最强的n只ETF"""
        top = signal.dropna().nlargest(n)
        return list(zip(top.index, top.values))

    def risk_parity_weights(self, selected_etfs: list,
                             lookback: int = 60) -> dict:
        """
        计算风险平价权重

        Parameters
        ----------
        selected_etfs : list
            [(etf_code, signal_value), ...]
        lookback : int
            用于计算波动率的回溯窗口
        """
        returns = self.data[list(zip(*selected_etfs))[0]].pct_change().iloc[-lookback:]

        # 逆波动率权重
        vols = returns.std()
        inv_vols = 1 / vols
        weights = inv_vols / inv_vols.sum()

        return weights.to_dict()
