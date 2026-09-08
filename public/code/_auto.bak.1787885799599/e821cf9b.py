# @quantlab/output: e821cf9b
class FactorAttribution:
    """因子归因分析"""

    def __init__(self, strategy_returns: pd.Series,
                 factor_returns: pd.DataFrame):
        """
        Parameters
        ----------
        strategy_returns : pd.Series
            策略日度收益
        factor_returns : pd.DataFrame
            因子日度收益，columns为因子名称
        """
        self.sr = strategy_returns
        self.fr = factor_returns

    def time_series_regression(self) -> dict:
        """时间序列回归归因"""
        import statsmodels.api as sm

        # 对齐数据
        common = self.sr.index.intersection(self.fr.index)
        X = self.fr.loc[common]
        y = self.sr.loc[common]

        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()

        return {
            'summary': model.summary().as_text(),
            'alpha': model.params['const'],
            'alpha_pvalue': model.pvalues['const'],
            'betas': model.params.drop('const').to_dict(),
            'r_squared': model.rsquared,
            'residuals': model.resid
        }

    def factor_exposure_decomposition(self) -> pd.DataFrame:
        """分解收益到各因子"""
        result = self.time_series_regression()

        decompositions = []
        for factor, beta in result['betas'].items():
            factor_contrib = beta * self.fr[factor].mean() * 252  # 年化
            decompositions.append({
                'factor': factor,
                'beta': beta,
                'annual_contribution': factor_contrib
            })

        df = pd.DataFrame(decompositions)
        df['contribution_pct'] = df['annual_contribution'] / \
                                  df['annual_contribution'].abs().sum() * 100
        return df.sort_values('contribution_pct', ascending=False)

    def rolling_factor_attribution(self, window: int = 60) -> pd.DataFrame:
        """滚动因子暴露分析：检测因子暴露的变化"""
        import statsmodels.api as sm

        common = self.sr.index.intersection(self.fr.index)
        sr = self.sr.loc[common]
        fr = self.fr.loc[common]

        rolling_betas = []
        for i in range(window, len(common)):
            X = fr.iloc[i-window:i]
            y = sr.iloc[i-window:i]
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()

            row = {'date': common[i]}
            row.update(model.params.to_dict())
            rolling_betas.append(row)

        return pd.DataFrame(rolling_betas).set_index('date')
