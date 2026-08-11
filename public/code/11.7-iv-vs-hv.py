"""11.7 隐含波动率 vs 历史波动率 — 5 种 HV 计算 + VIX 构造"""
import numpy as np
import pandas as pd

np.random.seed(2025)

# ===== 模拟 252 个交易日的价格序列 (年化波动率 22%) =====
n_days = 252
daily_vol = 0.22 / np.sqrt(252)
returns = np.random.randn(n_days) * daily_vol
price = 100 * np.exp(np.cumsum(returns))
log_returns = np.log(price[1:] / price[:-1])
print(f"模拟样本: {n_days} 天 年化波动率 22%")
print(f"实际log-ret std: {log_returns.std():.4f}")
print(f"实际年化vol: {log_returns.std()*np.sqrt(252)*100:.2f}%")


# ===== 1) 简单移动标准差 HV =====
def hv_simple(returns, window=20):
    """最常见：滚动 N 天年化波动率"""
    return returns.rolling(window).std() * np.sqrt(252)


# ===== 2) EWMA 指数加权波动率 (RiskMetrics) =====
def hv_ewma(returns, lam=0.94):
    """RiskMetrics 衰减因子 λ=0.94"""
    var = returns.var()
    vars_ = [var]
    for r in returns[1:]:
        new_var = lam * vars_[-1] + (1 - lam) * r ** 2
        vars_.append(new_var)
    return pd.Series(np.sqrt(vars_) * np.sqrt(252), index=returns.index)


# ===== 3) Parkinson (high-low) =====
def hv_parkinson(high, low, window=20):
    """利用日内最高最低估计波动率，比 close-to-close 高 ~5x 信息"""
    n = (np.log(high / low) ** 2) / (4 * np.log(2))
    return np.sqrt(n.rolling(window).mean() * 252)


# ===== 4) Garman-Klass (OHLC) =====
def hv_garman_klass(open_, high, low, close, window=20):
    """利用 OHLC 4 个价格"""
    n = 0.5 * (np.log(high / low) ** 2) - (2 * np.log(2) - 1) * (np.log(close / open_) ** 2)
    return np.sqrt(n.rolling(window).mean() * 252)


# ===== 5) Yang-Zhang (含隔夜跳空) =====
def hv_yang_zhang(open_, high, low, close, window=20):
    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    log_oc = (np.log(close / open_)) ** 2
    log_co = (np.log(close / open_.shift(1))) ** 2
    log_ho = (np.log(high / open_)) ** 2
    log_lo = (np.log(low / open_)) ** 2
    rs = log_ho * (log_ho - log_oc) + log_lo * (log_lo - log_oc)
    oc_var = log_oc.rolling(window).mean()
    co_var = log_co.rolling(window).mean()
    rs_var = rs.rolling(window).mean()
    var = oc_var + k * co_var + (1 - k) * rs_var
    return np.sqrt(var * 252)


# ===== 用真实 K 线模拟 OHLC =====
def synth_ohlc(close_price, vol_daily=0.014):
    """根据 close-price 模拟日内 OHLC"""
    n = len(close_price)
    daily_range = np.abs(np.random.randn(n)) * vol_daily * close_price
    close_prev = np.concatenate([[close_price[0]], close_price[:-1]])
    open_ = close_prev + np.random.randn(n) * vol_daily * close_price * 0.3
    high = np.maximum(open_, close_price) + np.abs(np.random.randn(n)) * daily_range * 0.5
    low = np.minimum(open_, close_price) - np.abs(np.random.randn(n)) * daily_range * 0.5
    return pd.Series(open_, index=close_price.index), \
           pd.Series(high, index=close_price.index), \
           pd.Series(low, index=close_price.index), \
           pd.Series(close_price, index=close_price.index)

idx = pd.date_range("2024-01-02", periods=n_days, freq="B")
close = pd.Series(price, index=idx)
open_, high, low, close = synth_ohlc(close)

# ===== 计算 5 种 HV 并对比 =====
results = pd.DataFrame()
results["HV_simple"] = hv_simple(pd.Series(log_returns, index=idx[1:]), 20)
results["HV_ewma"] = hv_ewma(pd.Series(log_returns, index=idx[1:]))
results["HV_parkinson"] = hv_parkinson(high, low, 20)
results["HV_gk"] = hv_garman_klass(open_, high, low, close, 20)
results["HV_yz"] = hv_yang_zhang(open_, high, low, close, 20)

print("\n" + "=" * 60)
print("【1】5 种 HV 在最新一天的水平 (年化)")
print("=" * 60)
last_hv = results.iloc[-1] * 100
for name, val in last_hv.items():
    print(f"  {name:<15}: {val:6.2f}%")

# ===== 6) VIX 指数构造 (CBOE 简化版) =====
print("\n" + "=" * 60)
print("【2】VIX 指数简化构造 (近期 + 远期 OTM-Put 加权)")
print("=" * 60)
# 模拟 30 天的 OTM Put 报价与 delta 间隔
def vix_approx(otm_puts_near, otm_puts_far, T1=1/12, T2=2/12):
    """otm_puts: list of (K, mid_price, delta_K)"""
    sigma2_near = (2/T1) * sum(p[1] * (p[2]/p[0]**2) for p in otm_puts_near)
    sigma2_far  = (2/T2) * sum(p[1] * (p[2]/p[0]**2) for p in otm_puts_far)
    vix2 = ((T1*sigma2_near*(sigma2_far - sigma2_near*0)/(sigma2_far-sigma2_near))
           + (T2*sigma2_far - T1*sigma2_near)/(sigma2_far - sigma2_near))
    return np.sqrt(vix2) * 100

otm_near = [(98, 0.30, 1), (95, 0.15, 3), (90, 0.06, 5)]
otm_far  = [(98, 0.65, 1), (95, 0.35, 3), (90, 0.18, 5)]
vix_now = vix_approx(otm_near, otm_far, 1/12, 2/12)
print(f"  VIX 估算: {vix_now:.2f}  (基于近月/次月 OTM Put)")
print(f"  历史分位数(<20:平静 / 20-30:正常 / >30:紧张): 当前在{'紧张' if vix_now>30 else '正常'}区间")
