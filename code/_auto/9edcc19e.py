# @quantlab/output: 9edcc19e
import akshare as ak
import pandas as pd

def fetch_50etf_options():
    """获取 50ETF 期权 T 型报价"""
    try:
        # 获取 50ETF 期权日线
        df = ak.option_finance_board(underlying="华夏上证50ETF期权", order_by="持仓量")
        return df
    except Exception as e:
        print(f"akshare 接口变动, 推荐使用 Get_Option_Func CSVDailyData")
        return None

def iv_calc_from_quote(S, K, T, r, market_price, otype="call"):
    """牛顿迭代反推隐含波动率"""
    from scipy.stats import norm
    sigma = 0.20
    for _ in range(50):
        d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        if otype == "call":
            bs = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        else:
            bs = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
        vega = S*np.exp(-d1**2/2)/np.sqrt(2*np.pi)*np.sqrt(T) / 100
        if abs(bs - market_price) < 1e-5:
            break
        sigma -= (bs - market_price) / vega
    return sigma

# 示例: 3 个不同行权价的市场报价反推 IV
market_data = [
    (2.700, 0.1215, "call"),  # ITM
    (2.800, 0.0465, "call"),  # ATM
    (2.900, 0.0090, "call"),  # OTM
]
S = 2.800
T = 30/365
print(f"{'行权价':>8} {'市价':>8} {'隐含IV':>8} {'类型':>6}")
print("-" * 32)
for K, mp, otype in market_data:
    iv = iv_calc_from_quote(S, K, T, 0.025, mp, otype)
    print(f"{K:8.3f} {mp:8.4f} {iv*100:7.2f}% {otype:>6}")
