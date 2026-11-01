# @quantlab/output: 3ef351dd
class EventDrivenBacktest:
    def __init__(self, initial_capital=1_000_000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = {}
        self.equity_curve = []
        self.trades = []

    def on_bar(self, timestamp, prices, signals):
        # 处理信号并生成订单
        for symbol, target_weight in signals.items():
            current_value = self.position.get(symbol, 0) * prices[symbol]
            target_value = self.cash * target_weight
            trade_value = target_value - current_value
            if abs(trade_value) > 1000:  # 最小交易金额
                self.execute_order(timestamp, symbol, trade_value, prices[symbol])
        self.update_equity(timestamp, prices)

    def execute_order(self, timestamp, symbol, value, price):
        qty = int(value / price)
        if qty == 0:
            return
        cost = abs(qty * price) * 0.001  # 手续费
        self.cash -= value + cost
        self.position[symbol] = self.position.get(symbol, 0) + qty
        self.trades.append({
            'timestamp': timestamp, 'symbol': symbol,
            'qty': qty, 'price': price, 'cost': cost
        })

    def update_equity(self, timestamp, prices):
        total_value = self.cash + sum(
            qty * prices.get(sym, 0) for sym, qty in self.position.items()
        )
        self.equity_curve.append({'timestamp': timestamp, 'equity': total_value})

# 使用示例
engine = EventDrivenBacktest(initial_capital=1_000_000)
for timestamp, row in market_data.iterrows():
    signals = strategy.generate_signals(timestamp)
    engine.on_bar(timestamp, row['prices'], signals)
