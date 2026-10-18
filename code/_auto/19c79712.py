# @quantlab/output: 19c79712
def rolling_factor_calculation(data: pd.DataFrame) -> pd.DataFrame:
    """
    计算常用的滚动因子

    演示如何用 rolling + transform 高效计算
    """
    df = data.copy()

    # 动量因子：最近20日累计收益
    df['momentum_20d'] = df.groupby('code')['close'].transform(
        lambda x: x.pct_change(20, fill_method=None)
    )

    # 波动率因子：最近20日收益标准差
    df['volatility_20d'] = df.groupby('code')['close'].transform(
        lambda x: x.pct_change().rolling(20).std()
    )

    # 换手率加权因子：最近5日与20日成交量的比值
    df['volume_ratio'] = df.groupby('code')['volume'].transform(
        lambda x: x.rolling(5).mean() / x.rolling(20).mean()
    )

    # 截面排名（cross-sectional rank）
    for col in ['momentum_20d', 'volatility_20d', 'volume_ratio']:
        df[f'{col}_rank'] = df.groupby('date')[col].rank(pct=True)

    return df
