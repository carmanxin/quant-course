# @quantlab/output: 6cd1d8e1
def detect_lookahead_bias(factor_df, price_df, shift_days=1):
    """
    检查因子值是否能用未来收益率预测当期值（如果能够，说明有前视偏差）
    """
    future_returns = price_df.pct_change(shift_days).shift(-shift_days)

    from scipy.stats import spearmanr
    corr = factor_df.corrwith(future_returns, axis=1)

    # 如果因子与未来收益高度相关，而因子声称是当下可计算的...有问题
    return corr

# 正确的做法：因子必须基于已知信息
def correct_factor_construction(data, date):
    # 使用 date 之前的数据构建因子
    historical_data = data[data.index <= date]
    factor_value = compute_factor_using_only_historical(historical_data)
    return factor_value
