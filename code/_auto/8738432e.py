# @quantlab/output: 8738432e
import numpy as np
import pandas as pd
from typing import List, Tuple


class BrinsonAttribution:
    """Brinson 绩效归因分析"""

    def __init__(self, portfolio_weights: pd.DataFrame,
                 benchmark_weights: pd.DataFrame,
                 portfolio_returns: pd.DataFrame,
                 benchmark_returns: pd.DataFrame):
        """
        Parameters
        ----------
        portfolio_weights : pd.DataFrame
            组合在各板块的权重，index=日期，columns=板块
        benchmark_weights : pd.DataFrame
            基准在各板块的权重
        portfolio_returns : pd.DataFrame
            组合中各板块的收益
        benchmark_returns : pd.DataFrame
            基准中各板块的收益
        """
        self.pw = portfolio_weights
        self.bw = benchmark_weights
        self.pr = portfolio_returns
        self.br = benchmark_returns

    def decompose(self) -> dict:
        """执行 Brinson 分解"""
        # 确保对齐
        common_dates = self.pw.index.intersection(self.bw.index)\
                                     .intersection(self.pr.index)\
                                     .intersection(self.br.index)

        pw = self.pw.loc[common_dates]
        bw = self.bw.loc[common_dates]
        pr = self.pr.loc[common_dates]
        br = self.br.loc[common_dates]

        # 总超额收益
        portfolio_total = (pw * pr).sum(axis=1)
        benchmark_total = (bw * br).sum(axis=1)
        total_excess = portfolio_total - benchmark_total

        # 配置效应：权重差异 * 基准收益
        allocation = ((pw - bw) * br).sum(axis=1)

        # 选择效应：基准权重 * 收益差异
        selection = (bw * (pr - br)).sum(axis=1)

        # 交互效应：权重差异 * 收益差异
        interaction = ((pw - bw) * (pr - br)).sum(axis=1)

        # 按板块分解
        sector_allocation = (pw - bw) * br
        sector_selection = bw * (pr - br)
        sector_interaction = (pw - bw) * (pr - br)

        return {
            'total_excess_return': total_excess,
            'allocation_effect': allocation,
            'selection_effect': selection,
            'interaction_effect': interaction,
            'sector_allocation': sector_allocation,
            'sector_selection': sector_selection,
            'sector_interaction': sector_interaction
        }

    def summary_report(self) -> str:
        """生成归因摘要报告"""
        result = self.decompose()

        # 年化累计
        total_cum = result['total_excess_return'].cumsum()
        alloc_cum = result['allocation_effect'].cumsum()
        select_cum = result['selection_effect'].cumsum()
        interact_cum = result['interaction_effect'].cumsum()

        report = []
        report.append("=" * 60)
        report.append("           Brinson 绩效归因报告")
        report.append("=" * 60)
        report.append("")
        report.append(f"【归因周期】{total_cum.index[0].strftime('%Y-%m-%d')} 至 {total_cum.index[-1].strftime('%Y-%m-%d')}")
        report.append(f"【交易日数】{len(total_cum)}天")
        report.append("")
        report.append("【累计效应分解】")
        report.append(f"  配置效应: {alloc_cum.iloc[-1]:.4%}")
        report.append(f"  选择效应: {select_cum.iloc[-1]:.4%}")
        report.append(f"  交互效应: {interact_cum.iloc[-1]:.4%}")
        report.append(f"  总超额收益: {total_cum.iloc[-1]:.4%}")
        report.append("")

        # 各效应的波动率
        report.append("【效应稳定性】")
        report.append(f"  配置效应日波动: {alloc_cum.diff().std():.4%}")
        report.append(f"  选择效应日波动: {select_cum.diff().std():.4%}")
        report.append("")

        # 信息比率
        tracking_error = result['total_excess_return'].std()
        info_ratio = result['total_excess_return'].mean() / tracking_error if tracking_error > 0 else 0
        report.append(f"【信息比率】{info_ratio:.2f}")

        return '\n'.join(report)

    def sector_attribution_heatmap(self) -> pd.DataFrame:
        """生成板块归因热力图数据"""
        result = self.decompose()

        total_by_sector = result['sector_allocation'].sum() + \
                          result['sector_selection'].sum() + \
                          result['sector_interaction'].sum()

        return pd.DataFrame({
            'allocation': result['sector_allocation'].sum(),
            'selection': result['sector_selection'].sum(),
            'interaction': result['sector_interaction'].sum(),
            'total': total_by_sector
        }).sort_values('total', ascending=False)
