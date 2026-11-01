# @quantlab/output: b9ea93d8
import numpy as np
import pandas as pd
from scipy import stats

class RiskMetrics:
    def __init__(self, returns, confidence_levels=[0.95, 0.99]):
        """
        Parameters:
            returns: pd.Series, 日收益率
            confidence_levels: 置信水平列表
        """
        self.returns = returns
        self.alpha_levels = confidence_levels

    def var_parametric(self, horizon=1):
        """参数法VaR（假设正态分布）"""
        mu = self.returns.mean()
        sigma = self.returns.std()

        results = {}
        for alpha in self.alpha_levels:
            z_score = stats.norm.ppf(1 - alpha)
            var = -(mu * horizon + sigma * np.sqrt(horizon) * z_score)
            results[f'VaR_{int(alpha*100)}%'] = var

        return results

    def var_historical(self, horizon=1):
        """历史模拟法VaR"""
        horizon_returns = self.returns.rolling(horizon).sum().dropna()

        results = {}
        for alpha in self.alpha_levels:
            var = -np.percentile(horizon_returns, (1 - alpha) * 100)
            results[f'VaR_{int(alpha*100)}%'] = var

        return results

    def var_cvar_monte_carlo(self, n_simulations=10000, horizon=1):
        """蒙特卡洛法VaR和CVaR"""
        # 用t分布拟合（比正态分布更好地捕捉肥尾）
        t_df, t_loc, t_scale = stats.t.fit(self.returns)

        simulated_returns = stats.t.rvs(t_df, t_loc, t_scale,
                                        size=(n_simulations, horizon))

        if horizon > 1:
            simulated_returns = simulated_returns.sum(axis=1)

        results = {}
        for alpha in self.alpha_levels:
            # VaR
            var = -np.percentile(simulated_returns, (1 - alpha) * 100)
            results[f'VaR_{int(alpha*100)}%'] = var

            # CVaR (Expected Shortfall)
            tail = simulated_returns[simulated_returns <= -var]
            cvar = -tail.mean() if len(tail) > 0 else var
            results[f'CVaR_{int(alpha*100)}%'] = cvar

        return results

    def full_risk_report(self):
        """完整的风险报告"""
        report = {}

        # 基础统计
        report['mean_daily'] = self.returns.mean()
        report['std_daily'] = self.returns.std()
        report['skewness'] = self.returns.skew()
        report['kurtosis'] = self.returns.kurtosis()
        report['min_daily'] = self.returns.min()

        # VaR/CVaR (1天)
        report.update({f'Parametric_{k}': v for k, v in self.var_parametric().items()})
        report.update({f'Historical_{k}': v for k, v in self.var_historical().items()})
        report.update({f'MC_{k}': v for k, v in self.var_cvar_monte_carlo().items()})

        # 10天VaR (sqrt(T)缩放)
        report.update({
            f'10d_Parametric_{k}': v * np.sqrt(10)
            for k, v in self.var_parametric().items()
        })

        return pd.Series(report)
