"""11.6 期权市场基础 — 合约规格与报价获取演示"""
import numpy as np
from scipy.stats import norm

# ===== 1) 50ETF 期权合约规格 =====
print("=" * 60)
print("【1】50ETF 期权主力合约规格")
print("=" * 60)
spec_50etf = {
    "合约标的": "上证50ETF (510050)",
    "合约单位": "10000份(1张)",
    "行权方式": "欧式",
    "到期月份": "当月/下月/当季/隔季",
    "行权价间距": "3元(3元以下1元,3-5元0.5元,5元以上1元)",
    "最小变动价位": "0.0001元",
    "涨跌停": "上一交易日结算价±10%(最后交易日±20%)",
    "交易时间": "9:30-11:30 / 13:00-15:00",
    "行权日": "到期月份的第四个星期三",
}
for k, v in spec_50etf.items():
    print(f"  {k:<12}: {v}")

# ===== 2) Black-Scholes 定价 + 隐含波动率反推 =====
print("\n" + "=" * 60)
print("【2】BS 定价与隐含波动率反推")
print("=" * 60)


def bs_price(S, K, T, r, sigma, otype="call"):
    """Black-Scholes 欧式期权定价"""
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if otype == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def implied_vol(market_price, S, K, T, r, otype="call"):
    """牛顿迭代法反推隐含波动率"""
    sigma = 0.2
    for _ in range(100):
        diff = bs_price(S, K, T, r, sigma, otype) - market_price
        if abs(diff) < 1e-6:
            return sigma
        # Vega 作为数值导数
        dS = sigma * 0.01
        vega = (bs_price(S, K, T, r, sigma + dS, otype)
                - bs_price(S, K, T, r, sigma - dS, otype)) / (2 * dS)
        sigma -= diff / vega
        if sigma <= 0:
            sigma = 0.001
    return sigma


# 场景: 50ETF 现价 2.800, ATM 行权价 2.800, 30天到期
S = 2.800
K = 2.800
T = 30 / 365
r = 0.025

# 期权市场报价 (3 个不同行权价)
market_data = [
    (2.700, 0.1215),  # ITM Call
    (2.800, 0.0465),  # ATM Call
    (2.900, 0.0090),  # OTM Call
]
print(f"标的: 50ETF  S={S}  T={T:.4f}年  r={r:.3f}")
print(f"{'行权价':>8} {'市价':>8} {'BS价':>8} {'隐含IV':>8}")
print("-" * 38)
for K_i, mp in market_data:
    iv = implied_vol(mp, S, K_i, T, r, "call")
    bs = bs_price(S, K_i, T, r, iv, "call")
    print(f"{K_i:8.3f} {mp:8.4f} {bs:8.4f} {iv*100:7.2f}%")

# ===== 3) 合约规模换算 =====
print("\n" + "=" * 60)
print("【3】一张 50ETF 期权实际持仓规模")
print("=" * 60)
opt_price = 0.0465      # 一份期权价格
contract_multiplier = 10000
one_lot_value = opt_price * contract_multiplier
print(f"  1份期权价格:           {opt_price:.4f} 元")
print(f"  合约乘数:             {contract_multiplier} 份")
print(f"  1张期权名义金额:       {one_lot_value:>8.2f} 元")
print(f"  对应标的ETF市值:       {S*contract_multiplier:>8.2f} 元")
print(f"  期权/标的价值比:       {opt_price/S*100:>8.2f}%")
