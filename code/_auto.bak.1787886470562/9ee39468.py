# @quantlab/output: 9ee39468
# 跨式组合(Straddle)的 Vega 叠加分析
straddle_vega = (
    bs_greeks(S=100, K=100, T=30/365, r=0.03, sigma=0.20, option_type='call')['vega']
    + bs_greeks(S=100, K=100, T=30/365, r=0.03, sigma=0.20, option_type='put')['vega']
)
print(f"跨式组合 Vega: {straddle_vega:.4f}  —— 每1%的IV变动带来的组合价值变动")
