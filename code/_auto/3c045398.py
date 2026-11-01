# @quantlab/output: 3c045398
def hv_simple(returns, window=20):
    """方法 1: 简单滚动标准差"""
    return returns.rolling(window).std() * np.sqrt(252)

def hv_ewma(returns, lam=0.94):
    """方法 2: RiskMetrics EWMA (λ=0.94 是业界标准)"""
    var = returns.var()
    vars_list = [var]
    for r in returns[1:]:
        var = lam * vars_list[-1] + (1-lam) * r**2
        vars_list.append(var)
    return pd.Series(np.sqrt(vars_list) * np.sqrt(252), index=returns.index)

def hv_parkinson(high, low, window=20):
    """方法 3: Parkinson (high-low)"""
    n = (np.log(high/low))**2 / (4*np.log(2))
    return np.sqrt(n.rolling(window).mean() * 252)

def hv_garman_klass(open_, high, low, close, window=20):
    """方法 4: Garman-Klass (OHLC)"""
    n = 0.5*(np.log(high/low))**2 - (2*np.log(2)-1)*(np.log(close/open_))**2
    return np.sqrt(n.rolling(window).mean() * 252)

def hv_yang_zhang(open_, high, low, close, window=20):
    """方法 5: Yang-Zhang (OHLC, 完整)"""
    k = 0.34 / (1.34 + (window+1)/(window-1))
    log_oc = np.log(close/open_)
    log_co = np.log(close/open_.shift(1))
    log_ho = np.log(high/open_)
    log_lo = np.log(low/open_)

    oc_var = (log_oc**2).rolling(window).mean()
    co_var = (log_co**2).rolling(window).mean()
    rs = log_ho*(log_ho-log_oc) + log_lo*(log_lo-log_oc)
    rs_var = rs.rolling(window).mean()

    var = oc_var + k*co_var + (1-k)*rs_var
    return np.sqrt(var * 252)

# 用 close 模拟 OHLC(实际应用应使用真实 K 线)
idx = pd.date_range("2024-01-01", periods=n_days)
close = pd.Series(np.asarray(prices).ravel(), index=idx)
noise = lambda size: np.abs(np.random.randn(size)) * 0.003 * pd.Series(prices['close'].iloc[:size].values if size<n_days else prices['close'].values, index=idx[:size] if size<n_days else idx)
# 简化:用 close 构造伪 OHLC
def synth_ohlc(close):
    n = len(close)
    open_ = close.shift(1) * (1 + np.random.randn(n)*0.005)
    high = close * (1 + np.abs(np.random.randn(n))*0.005)   # 保留 close 的 DatetimeIndex,避免 index 错位
    low  = close * (1 - np.abs(np.random.randn(n))*0.005)
    return open_, high, low, close

open_, high, low, close = synth_ohlc(close)

results = pd.DataFrame()
results["simple"]    = hv_simple(pd.Series(log_returns, index=idx[1:]), 20)
results["ewma"]      = hv_ewma(pd.Series(log_returns, index=idx[1:]))
results["parkinson"] = hv_parkinson(high, low, 20)
results["garman_k"]  = hv_garman_klass(open_, high, low, close, 20)
results["yang_z"]    = hv_yang_zhang(open_, high, low, close, 20)

print("\n最新一天的 5 种 HV (年化):")
print("-" * 50)
for name in results.columns:
    val = results[name].iloc[-1] * 100
    print(f"  {name:<12}: {val:6.2f}%")
