# @quantlab/output: 87c051b1
def global_macro_risk_parity(asset_returns: pd.DataFrame,
                              lookback: int = 252) -> pd.Series:
    """
    全球宏观风险平价组合权重。

    各资产权重 ∝ 1 / 波动率

    参数:
        asset_returns: 全球资产日收益率
        lookback: 波动率估计窗口
    返回:
        风险平价权重
    """
    # 滚动波动率
    rolling_vol = asset_returns.rolling(lookback).std().iloc[-1]

    # 权重 ∝ 1/vol
    inv_vol = 1.0 / rolling_vol
    weights = inv_vol / inv_vol.sum()

    # 波动率缩放：组合目标波动率 10%
    portfolio_vol_estimate = np.sqrt(
        weights @ asset_returns.rolling(lookback).cov().iloc[-1] @ weights
    )
    target_vol = 0.10 / np.sqrt(252)  # 日度目标波动率
    leverage = target_vol / portfolio_vol_estimate

    weights = weights * min(leverage, 2.0)  # 杠杆上限2倍

    return weights

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(37)
_rp_rets = pd.DataFrame(np.random.randn(500, 5) * 0.008,
                        columns=['美股', '美债', '黄金', '商品', '新兴市场'],
                        index=pd.date_range('2022-01-03', periods=500))
_rp = global_macro_risk_parity(_rp_rets)
print('风险平价权重:', _rp if not hasattr(_rp, 'to_string') else _rp.round(3).to_string())
