# @quantlab/output: 6136496a
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import akshare as ak  # 国内开源数据源，覆盖 A 股 + 部分全球指数

# 用 akshare 拉指数历史数据
# A 股指数（稳定可用）
A_SHARE = [
    ('sh000300', '沪深300'),
    ('sh000016', '上证50'),
    ('sh000905', '中证500'),
    ('sz399006', '创业板指'),
    ('sh000688', '科创50'),
]
# 全球指数（新浪源覆盖：标普500/纳斯达克/道琼斯）
GLOBAL = [
    ('.INX', '标普500'),
    ('.IXIC', '纳斯达克'),
    ('.DJI', '道琼斯'),
]

def fetch_zh(symbol, start='2020-01-01', end='2024-12-31'):
    df = ak.stock_zh_index_daily(symbol=symbol)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').loc[start:end]
    return df['close']

def fetch_us(symbol, start='2020-01-01', end='2024-12-31'):
    df = ak.index_us_stock_sina(symbol=symbol)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').loc[start:end]
    return df['close']

data = {}
for sym, name in A_SHARE:
    try:
        data[name] = fetch_zh(sym)
    except Exception as e:
        print(f"下载 {name} 失败: {e}")
for sym, name in GLOBAL:
    try:
        data[name] = fetch_us(sym)
    except Exception as e:
        print(f"下载 {name} 失败: {e}")

# 转累计收益（基期=1）
cumret = pd.DataFrame({n: (1 + p.pct_change()).cumprod() for n, p in data.items()}).dropna()

# 合并并可视化
cumret.plot(figsize=(12, 6), title='全球主要指数累计收益对比（2020-2024）')
plt.xlabel('日期')
plt.ylabel('累计净值')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# 计算各指数的年化指标
print('=' * 60)
print(f"{'指数':<10} {'年化收益':>10} {'年化波动':>10} {'夏普':>8} {'最大回撤':>10}")
print('-' * 60)
for name in cumret.columns:
    rets = cumret[name].pct_change().dropna()
    annual_ret = rets.mean() * 252
    annual_vol = rets.std() * np.sqrt(252)
    sharpe = annual_ret / annual_vol if annual_vol > 0 else 0
    max_dd = (cumret[name] / cumret[name].cummax() - 1).min()
    print(f"{name:<10} {annual_ret:>10.2%} {annual_vol:>10.2%} {sharpe:>8.2f} {max_dd:>10.2%}")
