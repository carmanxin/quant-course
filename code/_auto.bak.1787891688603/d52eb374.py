# @quantlab/output: d52eb374
def barra_style_factors(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """
    简化版 Barra 风格因子的构建。

    参数:
        fundamentals: 包含公司基本面数据的DataFrame
            列包括: size_log, book_to_price, momentum_12m1m,
                   beta, volatility, roe, eps_growth, leverage, dividend_yield
    返回:
        标准化后的风格因子暴露矩阵
    """
    factors = pd.DataFrame(index=fundamentals.index)

    # 1. 规模因子（Size）：市值的自然对数
    factors['Size'] = fundamentals['size_log']

    # 2. 价值因子（Value）：账面市值比
    factors['Value'] = fundamentals['book_to_price']

    # 3. 动量因子（Momentum）：12月-1月动量
    factors['Momentum'] = fundamentals['momentum_12m1m']

    # 4. 波动率因子（Volatility）：历史贝塔 + 残差波动率
    factors['Volatility'] = 0.6 * fundamentals['beta'] + \
                             0.4 * fundamentals['residual_volatility']

    # 5. 质量因子（Quality）：ROE + 盈利增长
    factors['Quality'] = 0.5 * fundamentals['roe'] + \
                          0.5 * fundamentals['eps_growth']

    # 6. 杠杆因子（Leverage）
    factors['Leverage'] = fundamentals['leverage']

    # 7. 成长因子（Growth）
    factors['Growth'] = fundamentals['eps_growth']

    # 8. 流动性因子（Liquidity）
    factors['Liquidity'] = fundamentals['turnover']

    # 9. 分红因子（Dividend Yield）
    factors['DividendYield'] = fundamentals['dividend_yield']

    # 标准化：使每个因子横截面均值为0，标准差为1
    for col in factors.columns:
        factors[col] = (factors[col] - factors[col].mean()) / \
                        factors[col].std()

    return factors
