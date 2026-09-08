# @quantlab/output: 7e2bb2d9
import statsmodels.api as sm

def neutralize_factor(factor_df, neutralizers):
    """
    因子中性化：剔除不需要的因子暴露

    Parameters:
        factor_df: pd.Series, 原始因子值
        neutralizers: pd.DataFrame, 需要中性化的因子（如行业哑变量、市值、Beta等）
    Returns:
        pd.Series, 中性化后的因子值
    """
    # 合并数据
    df = pd.DataFrame({'factor': factor_df, **neutralizers}).dropna()

    y = df['factor']
    X = sm.add_constant(df[neutralizers.keys()])

    # OLS回归取残差
    model = sm.OLS(y, X).fit()
    residuals = model.resid

    # 对残差做Z-score标准化
    neutralized = (residuals - residuals.mean()) / residuals.std()

    return neutralized

# 使用示例：将估值因子对行业和市值中性化
industry_dummies = pd.get_dummies(stock_industry).astype(float)
neutralizers = pd.DataFrame({
    'log_market_cap': np.log(market_cap),
    **industry_dummies
})
clean_factor = neutralize_factor(raw_value_factor, neutralizers)
