# @quantlab/output: c940c60f
import pandas as pd
import numpy as np
from scipy import stats

class FactorTester:
    def __init__(self, factor_df, return_df, periods=[1, 5, 21]):
        """
        factor_df: pd.DataFrame, index=date, columns=stock_codes, values=factor_value
        return_df: pd.DataFrame, forward returns, same structure
        """
        self.factor_df = factor_df
        self.return_df = return_df
        self.periods = periods

    def compute_ic(self):
        """计算Rank IC序列"""
        ic_results = {}
        for period in self.periods:
            fwd_return = self.return_df.shift(-period)
            ic = self.factor_df.corrwith(fwd_return, axis=1, method='spearman')
            ic_results[f'IC_{period}d'] = ic
        return pd.DataFrame(ic_results)

    def factor_quantile_returns(self, n_groups=10):
        """计算因子分位数组合的收益"""
        q = self.factor_df.rank(axis=1, pct=True)
        group = (q * n_groups).round()
        group = group.clip(1, n_groups)

        # 等权分组收益
        group_returns = {}
        for g in range(1, n_groups + 1):
            mask = (group == g)
            group_returns[g] = self.return_df[mask].mean(axis=1)
        return pd.DataFrame(group_returns)

    def ic_summary(self):
        """IC统计汇总"""
        ic_df = self.compute_ic()
        summary = pd.DataFrame({
            'IC_Mean': ic_df.mean(),
            'IC_Std': ic_df.std(),
            'ICIR': ic_df.mean() / ic_df.std(),
            'IC>0_ratio': (ic_df > 0).mean(),
            't_stat': ic_df.mean() / (ic_df.std() / np.sqrt(len(ic_df)))
        })
        return summary

    def factor_correlation_matrix(self, other_factors):
        """计算因子间的相关性矩阵"""
        all_factors = {'target': self.factor_df.stack()}
        for name, factor in other_factors.items():
            all_factors[name] = factor.stack()
        combined = pd.DataFrame(all_factors).dropna()
        return combined.corr()
