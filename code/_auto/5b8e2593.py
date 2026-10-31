# @quantlab/output: 5b8e2593
# 这是 NautilusTrader 风格的事件驱动 demo,展示其 API 设计哲学
# 注意:实际运行需 pip install nautilus_trader + rustc 编译

from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.orders import MarketOrder

class MyMAStrategy(Strategy):
    """NautilusTrader 的事件驱动策略"""

    def on_start(self):
        self.fast_ma_period = 10
        self.slow_ma_period = 50
        self.fast_values = []
        self.slow_values = []
        self.position = 0

    def on_bar(self, bar: Bar):
        # 累计 MA
        close = float(bar.close)
        self.fast_values.append(close)
        self.slow_values.append(close)
        if len(self.fast_values) > self.fast_ma_period:
            self.fast_values.pop(0)
        if len(self.slow_values) > self.slow_ma_period:
            self.slow_values.pop(0)

        if len(self.fast_values) < self.fast_ma_period:
            return
        if len(self.slow_values) < self.slow_ma_period:
            return

        fast_ma = sum(self.fast_values) / len(self.fast_values)
        slow_ma = sum(self.slow_values) / len(self.slow_values)

        # 事件循环:每根 K 线触发一次策略逻辑
        if self.position == 0 and fast_ma > slow_ma:
            # 上穿 → 开多
            order = MarketOrder(
                side=OrderSide.BUY,
                quantity=self.strategy_config.qty,
                instrument_id=bar.bar_type.instrument_id,
                time_in_force=TimeInForce.DAY,
            )
            self.submit_order(order)
            self.position = 1
        elif self.position == 1 and fast_ma < slow_ma:
            # 下穿 → 平多
            order = MarketOrder(
                side=OrderSide.SELL,
                quantity=self.strategy_config.qty,
                instrument_id=bar.bar_type.instrument_id,
                time_in_force=TimeInForce.DAY,
            )
            self.submit_order(order)
            self.position = 0
