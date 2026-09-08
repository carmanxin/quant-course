# @quantlab/output: 308e65a2
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class MultiFactorStrategy:
    def __init__(self, factors_config, synthesis_method='icir', stock_num=50):
        """
        factors_config: dict, {factor_name: factor_series}
        synthesis_method: 'equal', 'icir', or 'optimize'
        stock_num: 持仓股票数
        """
        self.factors = factors_config
        self.method = synthesis_method
        self.stock_num = stock_num
        self.factor_weights = None
        self.ic_history = {}

    def compute_factor_ic(self, factor, forward_returns, window=None):
        """计算因子的滚动Rank IC"""
        from scipy.stats import spearmanr

        if window:
            ic = factor.rolling(window).apply(
                lambda f: spearmanr(f, forward_returns.loc[f.index])[0]
                if len(f.dropna()) > 10 else np.nan
            )
        else:
            ic = spearmanr(factor.dropna(), forward_returns.loc[factor.dropna().index])[0]
        return ic

    def preprocess_factors(self, date):
        """因子预处理：去极值、中性化、标准化"""
        processed = {}

        for name, factor in self.factors.items():
            f = factor.copy()

            # 1. 中位数去极值（MAD法）
            median = f.median()
            mad = np.median(np.abs(f - median))
            upper = median + 5 * mad
            lower = median - 5 * mad
            f = f.clip(lower, upper)

            # 2. 行业和市值中性化（见5.1节）
            # f = neutralize_factor(f, industry_dummies, market_cap)

            # 3. Z-score标准化（截尾）
            f = (f - f.mean()) / f.std()
            f = f.clip(-3, 3)

            processed[name] = f

        return pd.DataFrame(processed)

    def factor_synthesis(self, processed_factors):
        """因子合成"""
        if self.method == 'equal':
            if self.factor_weights is None:
                n = len(processed_factors.columns)
                self.factor_weights = pd.Series(1/n, index=processed_factors.columns)
            composite = processed_factors.mul(self.factor_weights).sum(axis=1)

        elif self.method == 'icir':
            if self.factor_weights is None:
                # 使用历史IC计算ICIR
                icirs = {}
                for name, factor in self.factors.items():
                    ic_mean = self.ic_history.get(f'{name}_mean', 0.01)
                    ic_std = self.ic_history.get(f'{name}_std', 0.05)
                    icirs[name] = ic_mean / ic_std
                total_icir = sum(icirs.values())
                self.factor_weights = pd.Series(
                    {k: v/total_icir for k, v in icirs.items()}
                )
            composite = processed_factors.mul(self.factor_weights).sum(axis=1)

        elif self.method == 'optimize':
            # 最大化复合因子的预期ICIR
            # 简化版：使用IC协方差矩阵的逆做权重
            ic_means = np.array([self.ic_history.get(f'{n}_mean', 0.01)
                                 for n in processed_factors.columns])
            # 假设IC间相关性为0.3
            n = len(ic_means)
            ic_cov = np.eye(n) * 0.05**2
            ic_cov[ic_cov == 0] = 0.3 * 0.05 * 0.05  # off-diagonal

            np.fill_diagonal(ic_cov, 0.05**2)
            weights = np.linalg.inv(ic_cov).dot(ic_means)
            weights = np.maximum(weights, 0)  # 非负约束
            weights = weights / weights.sum()
            self.factor_weights = pd.Series(weights, index=processed_factors.columns)

            composite = processed_factors.mul(self.factor_weights).sum(axis=1)

        return composite

    def generate_portfolio(self, composite_score, prices, capital):
        """基于复合得分生成投资组合"""
        # 选取得分最高的stock_num只股票
        selected = composite_score.nlargest(self.stock_num)
        selected = selected[selected.index.isin(prices.columns)]

        if len(selected) == 0:
            return {}

        # 等权配置（简化）
        weight_per_stock = 1.0 / len(selected)
        portfolio = {}
        for stock in selected.index:
            portfolio[stock] = capital * weight_per_stock / prices[stock]

        return portfolio
