# @quantlab/output: dc21f062
import time
import pandas as pd
import numpy as np

def benchmark_frameworks(n_params=200):
    """横评 vectorbt vs Backtrader 在参数网格扫描下的速度"""
    # 生成固定数据
    np.random.seed(0)
    n_days = 1500
    # vectorbt 要求 fixed frequency,使用 date_range 不用 bdate_range(B 非 fixed)
    dates = pd.date_range('2020-01-01', periods=n_days, freq='D')
    close = 100 * np.exp(np.cumsum(np.random.normal(0.0003, 0.02, n_days)))
    df = pd.DataFrame({'close': close}, index=dates)

    # vectorbt 扫描(short=5..50, long=20..200 步长=5)
    import vectorbt as vbt
    short_windows = list(range(5, 55, 5))
    long_windows = list(range(20, 205, 10))

    t0 = time.time()
    combos = []
    for sw in short_windows:
        s_ma = vbt.MA.run(df['close'], window=sw)
        for lw in long_windows:
            if sw >= lw:
                continue
            l_ma = vbt.MA.run(df['close'], window=lw)
            entries = s_ma.ma_crossed_above(l_ma)
            exits = s_ma.ma_crossed_below(l_ma)
            pf = vbt.Portfolio.from_signals(close=df['close'],
                                            entries=entries, exits=exits,
                                            init_cash=1_000_000, fees=0.0003)
            combos.append({
                'short': sw, 'long': lw,
                'sharpe': pf.sharpe_ratio(),
                'total_return': pf.total_return()
            })
    vectorbt_time = time.time() - t0
    print(f"vectorbt 扫描 {len(combos)} 个组合: {vectorbt_time:.2f}s")

    # Backtrader 的扫描相对慢,这里仅做 20 组示意
    import backtrader as bt

    class ParamStrategy(bt.Strategy):
        params = (('short', 10), ('long', 50))

        def __init__(self):
            self.s = bt.indicators.SMA(self.data.close, period=self.p.short)
            self.l = bt.indicators.SMA(self.data.close, period=self.p.long)

        def next(self):
            if not self.position and self.s[0] > self.l[0] and self.s[-1] <= self.l[-1]:
                self.buy()
            elif self.position and self.s[0] < self.l[0]:
                self.close()

    t0 = time.time()
    bt_combos = []
    ohlcv = pd.DataFrame({
        'open': df['close'].shift(1).fillna(df['close'].iloc[0]),
        'high': df['close'], 'low': df['close'],
        'close': df['close'], 'volume': 1_000_000,
    }, index=dates)
    ohlcv.columns = [c.capitalize() for c in ohlcv.columns]

    n_bt = 0
    for sw in [5, 10, 15, 20, 25]:
        for lw in [30, 50, 70, 90]:
            if sw >= lw:
                continue
            cerebro = bt.Cerebro(stdstats=False)
            cerebro.addstrategy(ParamStrategy, short=sw, long=lw)
            cerebro.broker.setcash(1_000_000)
            data = bt.feeds.PandasData(dataname=ohlcv)
            cerebro.adddata(data)
            result = cerebro.run()[0]
            bt_combos.append({'short': sw, 'long': lw})
            n_bt += 1
    bt_time = time.time() - t0

    print(f"Backtrader 扫描 {n_bt} 个组合: {bt_time:.2f}s")
    print(f"平均每个组合: {bt_time / n_bt:.3f}s (Backtrader) vs "
          f"{vectorbt_time / len(combos):.4f}s (vectorbt)")

    return vectorbt_time, bt_time, n_bt, len(combos)

v_time, bt_time, n_bt, n_vbt = benchmark_frameworks()
print(f"\n加速比(vectorbt / Backtrader) ≈ {(bt_time/n_bt) / (v_time/n_vbt):.1f}x")
