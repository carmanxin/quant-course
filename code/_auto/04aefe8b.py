# @quantlab/output: 04aefe8b
import numpy as np
import pandas as pd
from scipy import stats


class IPOReturnAnalyzer:
    """A股打新收益率分析框架"""

    def __init__(self, ipo_data: pd.DataFrame):
        """
        Parameters
        ----------
        ipo_data : pd.DataFrame
            IPO数据库，包含每只新股的发行信息、配售结果和上市表现
            columns: ['code', 'name', 'ipo_date', 'list_date', 'issue_price',
                     'online_lottery_rate', 'offline_alloc_ratio',
                     'first_day_open', 'first_day_close', 'first_day_high',
                     'n_consecutive_limits', 'open_price_on_break',
                     'is_break', 'market', 'board',
                     'pe_ratio', 'pb_ratio']
        """
        self.data = ipo_data

    def online_return_analysis(self, ticket_capital: float = 300000,
                                sh_market: float = 150000,
                                sz_market: float = 150000) -> dict:
        """
        分析网上打新的收益率

        Parameters
        ----------
        ticket_capital : float
            总门票市值
        sh_market : float
            上海市值（用于沪市打新）
        sz_market : float
            深圳市值（用于深市打新）
        """
        df = self.data.copy()

        # 每只新股的网上申购上限
        if 'online_max_lots' in df.columns:
            df['max_lots'] = df['online_max_lots']
        else:
            df['max_lots'] = 10000  # 默认假设

        # 每只新股的收益（以首日开盘价计算）
        df['first_day_return'] = df['first_day_open'] / df['issue_price'] - 1

        # 每只新股的期望收益 = 中签率 * 首日收益 * 中签股数
        df['lottery_rate'] = df['online_lottery_rate']
        df['expected_return_per_ipo'] = (
            df['lottery_rate'] *
            df['first_day_return'] *
            500  # 每签500股
        )

        # 按市场分类
        sh_ipos = df[df['market'] == 'SH']
        sz_ipos = df[df['market'] == 'SZ']

        total_expected = df['expected_return_per_ipo'].sum()

        # 年化收益率
        n_years = (df['list_date'].max() - df['list_date'].min()).days / 365
        if n_years <= 0:
            n_years = 1

        annual_return = total_expected / ticket_capital / n_years

        return {
            'total_expected_return': total_expected,
            'annual_return_pct': annual_return * 100,
            'n_ipos': len(df),
            'n_sh': len(sh_ipos),
            'n_sz': len(sz_ipos),
            'avg_first_day_return': df['first_day_return'].mean(),
            'median_first_day_return': df['first_day_return'].median(),
            'break_rate': df['is_break'].mean() if 'is_break' in df.columns else 0,
            'sh_annual_return': sh_ipos['expected_return_per_ipo'].sum() / sh_market / n_years if sh_market > 0 else 0,
            'sz_annual_return': sz_ipos['expected_return_per_ipo'].sum() / sz_market / n_years if sz_market > 0 else 0
        }

    def offline_return_analysis(self, subscription_capital: float = 50_000_000) -> dict:
        """
        网下打新收益率分析
        """
        df = self.data.copy()

        # 网下配售比例
        df['offline_alloc_amount'] = df['issue_price'] * df['offline_alloc_ratio'] * \
                                      df.get('total_shares', 0)

        # 首日收益（考虑可能的锁定期折价）
        lockup_months = df.get('lockup_period', 0).fillna(0)
        df['lockup_discount'] = 1.0 - 0.005 * lockup_months  # 每月0.5%的流动性折价

        df['offline_return'] = (
            df['first_day_return'] *
            df['offline_alloc_amount'] *
            df['lockup_discount']
        )

        df['expected_offline_return'] = df['offline_return']  # 网下配售比例替代了中签率

        total_return = df['expected_offline_return'].sum()
        n_years = (df['list_date'].max() - df['list_date'].min()).days / 365
        if n_years <= 0:
            n_years = 1

        return {
            'total_return': total_return,
            'annual_return_pct': total_return / subscription_capital / n_years * 100,
            'return_on_capital': total_return / subscription_capital,
            'n_ipos_participated': len(df)
        }
