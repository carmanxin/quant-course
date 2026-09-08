# @quantlab/output: e816cdd3
import backtrader as bt
import pandas as pd
import numpy as np

class DoubleMAStrategy(bt.Strategy):
    """双均线策略:短均线上穿长均线买入,下穿卖出"""
    params = (
        ('short_period', 10),
        ('long_period', 50),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SMA(self.data.close, period=self.p.short_period)
        self.long_ma = bt.indicators.SMA(self.data.close, period=self.p.long_period)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:  # 上穿
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])  # 95% 仓位
                self.buy(size=size)
        else:
            if self.crossover < 0:  # 下穿
                self.close()

# 准备数据(同上例相同的随机价格序列)
np.random.seed(42)
n_days = 1000
dates = pd.bdate_range('2022-01-01', periods=n_days)
close = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, n_days)))
df = pd.DataFrame({'close': close}, index=dates)

# backtrader 需要 DataFrame 包含 OHLCV,这里构造
ohlcv = pd.DataFrame({
    'open': df['close'].shift(1).fillna(df['close'].iloc[0]),
    'high': df['close'] * 1.01,
    'low': df['close'] * 0.99,
    'close': df['close'],
    'volume': np.random.randint(1_000_000, 5_000_000, n_days),
}, index=dates)
ohlcv.columns = [c.capitalize() if isinstance(c, str) else c for c in ohlcv.columns]

data_feed = bt.feeds.PandasData(dataline=ohlcv.reset_index().values,
                                  datetime=0, open=1, high=2, low=3, close=4, volume=5)

# 配置回测引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(DoubleMAStrategy)
cerebro.adddata(data_feed)
cerebro.broker.setcash(1_000_000)
cerebro.broker.setcommission(commission=0.0003, stamp_duty=0.001)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.025)
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

# 执行回测
results = cerebro.run()
strat = results[0]

print(f"最终净值: {cerebro.broker.getvalue():,.0f}")
print(f"夏普比率: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
print(f"最大回撤: {strat.analyzers.drawdown.get_analysis().max.drawdown:.2f}%")
trade_analysis = strat.analyzers.trades.get_analysis()
print(f"总交易次数: {trade_analysis.total.total}")
print(f"胜率: {trade_analysis.won.total / max(trade_analysis.total.total, 1):.1%}")
