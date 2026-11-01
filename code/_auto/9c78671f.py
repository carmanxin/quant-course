# @quantlab/output: 9c78671f
"""
事件驱动回测引擎 v1.0
QuantLab 课程 4.7 节示例

模块组成:
1. Event 类族         - 定义 5 种事件类型
2. DataHandler        - 历史数据 / 实时数据接入
3. Strategy           - 策略信号生成
4. Portfolio          - 持仓与订单管理
5. RiskManager        - 风控检查
6. ExecutionHandler   - 模拟撮合
7. BacktestingEngine  - 主循环
8. Analyzer           - 绩效分析
"""

# ============================================================
# Part 1: 事件类族定义
# ============================================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from queue import PriorityQueue
from collections import defaultdict

class EventType(Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"

class OrderType(Enum):
    MARKET = "MKT"
    LIMIT = "LMT"
    STOP = "STP"

class Direction(Enum):
    LONG = 1
    SHORT = -1
    EXIT = 0

@dataclass(order=True)
class Event:
    timestamp: datetime
    event_type: EventType
    priority: int = field(compare=False)
    data: Dict[str, Any] = field(default_factory=dict, compare=False)

# ============================================================
# Part 2: DataHandler
# ============================================================

class DataHandler:
    """历史行情数据源"""

    def __init__(self, symbols: List[str], ohlcv_data: Dict[str, pd.DataFrame]):
        self.symbols = symbols
        self.data = ohlcv_data  # {symbol: DataFrame[OHLCV]}
        self.continue_backtest = True
        self.current_bar_idx = 0
        self.max_idx = max(len(d) for d in ohlcv_data.values()) - 1

    def update_bars(self) -> List[Event]:
        """为每个 symbol 在当前时间点生成 MarketEvent"""
        if self.current_bar_idx >= self.max_idx:
            self.continue_backtest = False
            return []

        events = []
        for symbol in self.symbols:
            bar = self.data[symbol].iloc[self.current_bar_idx]
            events.append(Event(
                timestamp=bar.name,
                event_type=EventType.MARKET,
                priority=1,
                data={
                    'symbol': symbol,
                    'open': float(bar['open']),
                    'high': float(bar['high']),
                    'low': float(bar['low']),
                    'close': float(bar['close']),
                    'volume': int(bar.get('volume', 0))
                }
            ))
        self.current_bar_idx += 1
        return events

# ============================================================
# Part 3: Strategy
# ============================================================

class Strategy:
    """双均线示例策略"""

    def __init__(self, symbols: List[str], fast_window: int = 10, slow_window: int = 30):
        self.symbols = symbols
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.bars = {s: [] for s in symbols}  # 历史 close

    def calculate_signals(self, event: Event) -> List[Event]:
        if event.event_type != EventType.MARKET:
            return []

        symbol = event.data['symbol']
        self.bars[symbol].append(event.data['close'])
        if len(self.bars[symbol]) < self.slow_window:
            return []

        recent = self.bars[symbol][-self.slow_window:]
        fast_ma = sum(recent[-self.fast_window:]) / self.fast_window
        slow_ma = sum(recent) / self.slow_window

        signals = []
        if fast_ma > slow_ma:
            signals.append(Event(
                timestamp=event.timestamp,
                event_type=EventType.SIGNAL,
                priority=2,
                data={'symbol': symbol, 'direction': Direction.LONG, 'strength': 1.0}
            ))
        elif fast_ma < slow_ma:
            signals.append(Event(
                timestamp=event.timestamp,
                event_type=EventType.SIGNAL,
                priority=2,
                data={'symbol': symbol, 'direction': Direction.EXIT, 'strength': 1.0}
            ))
        return signals

# ============================================================
# Part 4: Portfolio
# ============================================================

class Portfolio:
    """组合管理:持仓、现金、订单生成"""

    def __init__(self, initial_capital: float = 1_000_000, max_position_pct: float = 0.1):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = defaultdict(int)  # symbol -> shares
        self.holdings = defaultdict(float)  # symbol -> market value
        self.max_position_pct = max_position_pct
        self.current_prices = {}  # 最新成交价

    def update_holdings(self, event: Event):
        """收到 MarketEvent 更新持仓市值"""
        if event.event_type != EventType.MARKET:
            return
        symbol = event.data['symbol']
        price = event.data['close']
        self.current_prices[symbol] = price
        self.holdings[symbol] = self.positions[symbol] * price

    def naive_order_from_signal(self, event: Event, equity: float) -> Optional[Event]:
        """根据 SignalEvent 生成 OrderEvent"""
        if event.event_type != EventType.SIGNAL:
            return None

        symbol = event.data['symbol']
        direction = event.data['direction']
        price = self.current_prices[symbol]

        if direction == Direction.LONG and self.positions[symbol] == 0:
            # 限价单:开仓到目标权重 max_position_pct
            target_value = equity * self.max_position_pct
            qty = int(target_value / price)
            if qty <= 0:
                return None
            return Event(
                timestamp=event.timestamp,
                event_type=EventType.ORDER,
                priority=3,
                data={
                    'symbol': symbol,
                    'qty': qty,
                    'order_type': OrderType.MARKET,
                    'direction': 'BUY',
                    'limit_price': None,
                }
            )
        elif direction == Direction.EXIT and self.positions[symbol] > 0:
            qty = self.positions[symbol]
            return Event(
                timestamp=event.timestamp,
                event_type=EventType.ORDER,
                priority=3,
                data={
                    'symbol': symbol,
                    'qty': qty,
                    'order_type': OrderType.MARKET,
                    'direction': 'SELL',
                    'limit_price': None,
                }
            )
        return None

    def update_fill(self, event: Event):
        """收到 FillEvent 后扣减现金、调整持仓"""
        if event.event_type != EventType.FILL:
            return
        symbol = event.data['symbol']
        qty = event.data['qty']
        fill_price = event.data['fill_price']
        commission = event.data['commission']

        if event.data['direction'] == 'BUY':
            self.cash -= qty * fill_price + commission
            self.positions[symbol] += qty
        else:  # SELL
            self.cash += qty * fill_price - commission
            self.positions[symbol] -= qty

    @property
    def equity(self) -> float:
        equity = self.cash
        for symbol, qty in self.positions.items():
            if qty != 0:
                equity += qty * self.current_prices.get(symbol, 0)
        return equity

# ============================================================
# Part 5: RiskManager
# ============================================================

class RiskManager:
    """风控:检查每笔订单是否符合规则"""

    def __init__(self, max_order_value: float = 100_000,
                 max_position_pct: float = 0.2,
                 max_drawdown_pct: float = 0.15):
        self.max_order_value = max_order_value
        self.max_position_pct = max_position_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.peak_equity = 0

    def check_order(self, order: Event, portfolio: Portfolio) -> bool:
        """返回 True 通过,False 拒绝"""
        if order.event_type != EventType.ORDER:
            return True

        symbol = order.data['symbol']
        qty = order.data['qty']
        price = portfolio.current_prices.get(symbol, 0)
        order_value = abs(qty) * price

        # 检查 1:单笔订单金额限制
        if order_value > self.max_order_value:
            print(f"[RISK] 订单金额 {order_value:.0f} 超过限制 {self.max_order_value}")
            return False

        # 检查 2:持仓占比限制
        equity = portfolio.equity
        if equity > 0:
            position_value = abs(qty) * price
            if position_value / equity > self.max_position_pct:
                print(f"[RISK] 持仓占比超限,调整订单数量")
                # 实际场景中应该调整 qty,这里简化拒绝
                return False

        # 检查 3:最大回撤熔断
        if equity > self.peak_equity:
            self.peak_equity = equity
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - equity) / self.peak_equity
            if drawdown > self.max_drawdown_pct:
                print(f"[RISK] 回撤 {drawdown:.2%} 超过熔断 {self.max_drawdown_pct:.0%} - 暂停新订单")
                return False

        return True

# ============================================================
# Part 6: ExecutionHandler
# ============================================================

class ExecutionHandler:
    """模拟撮合:接收 OrderEvent,模拟成交并返回 FillEvent"""

    def __init__(self, commission_rate: float = 0.0003,
                 stamp_duty: float = 0.001,
                 slippage_pct: float = 0.0005):
        self.commission_rate = commission_rate
        self.stamp_duty = stamp_duty
        self.slippage_pct = slippage_pct

    def execute_order(self, order: Event, market_event: Event) -> Optional[Event]:
        """市价单:按 close ± 滑点 立即成交"""
        if order.event_type != EventType.ORDER:
            return None

        symbol = order.data['symbol']
        qty = order.data['qty']
        direction = order.data['direction']
        order_type = order.data['order_type']

        if order_type == OrderType.MARKET:
            # 撮合价:close + 滑点(买入付+,卖出付-)
            close = market_event.data['close']
            slip = close * self.slippage_pct
            fill_price = close + slip if direction == 'BUY' else close - slip

            # 成本计算
            trade_value = abs(qty) * fill_price
            commission = max(trade_value * self.commission_rate, 5)  # 最低 5 元
            stamp = trade_value * self.stamp_duty if direction == 'SELL' else 0

            return Event(
                timestamp=order.timestamp,
                event_type=EventType.FILL,
                priority=4,
                data={
                    'symbol': symbol,
                    'qty': qty,
                    'fill_price': fill_price,
                    'direction': direction,
                    'commission': commission + stamp,
                    'slippage': abs(slip * qty),
                }
            )
        return None

# ============================================================
# Part 7: Analyzer
# ============================================================

import numpy as np

class Analyzer:
    """业绩分析:收集交易、计算净值曲线、计算夏普"""

    def __init__(self):
        self.equity_curve = []  # [(timestamp, equity)]
        self.trades = []        # 成交明细
        self.peak_equity = 0

    def record_equity(self, timestamp, equity):
        self.equity_curve.append((timestamp, equity))
        if equity > self.peak_equity:
            self.peak_equity = equity

    def record_fill(self, event: Event):
        self.trades.append({
            'timestamp': event.timestamp,
            'symbol': event.data['symbol'],
            'qty': event.data['qty'],
            'price': event.data['fill_price'],
            'commission': event.data['commission'],
        })

    def performance_report(self) -> Dict[str, Any]:
        if len(self.equity_curve) < 2:
            return {}

        df = pd.DataFrame(self.equity_curve, columns=['timestamp', 'equity'])
        df = df.set_index('timestamp')
        df['returns'] = df['equity'].pct_change().fillna(0)

        total_return = (df['equity'].iloc[-1] / self.equity_curve[0][1]) - 1
        n_days = len(df)
        ann_return = (1 + total_return) ** (252 / n_days) - 1
        ann_vol = df['returns'].std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0

        cummax = df['equity'].cummax()
        drawdown = (df['equity'] - cummax) / cummax
        max_dd = drawdown.min()

        return {
            'total_return': f"{total_return:.2%}",
            'ann_return': f"{ann_return:.2%}",
            'ann_vol': f"{ann_vol:.2%}",
            'sharpe': f"{sharpe:.2f}",
            'max_drawdown': f"{max_dd:.2%}",
            'total_trades': len(self.trades),
            'final_equity': f"{df['equity'].iloc[-1]:,.0f}",
        }

# ============================================================
# Part 8: BacktestingEngine 主循环
# ============================================================

class BacktestingEngine:
    """主循环:驱动所有模块按事件流运行"""

    def __init__(self, data_handler: DataHandler,
                 strategy: Strategy,
                 portfolio: Portfolio,
                 risk_manager: RiskManager,
                 execution_handler: ExecutionHandler,
                 analyzer: Analyzer):
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.risk_manager = risk_manager
        self.execution_handler = execution_handler
        self.analyzer = analyzer

    def run(self):
        """主循环:数据 → 信号 → 订单 → 撮合 → 持仓 → 记录"""
        market_events_buf = []

        while self.data_handler.continue_backtest:
            # Step 1: 取下一批 MarketEvent
            market_events = self.data_handler.update_bars()
            if not market_events:
                break

            market_events_buf = market_events

            # Step 2: 对每只 symbol 处理事件
            for mkt_event in market_events:
                # 先更新持仓市值
                self.portfolio.update_holdings(mkt_event)

                # 策略生成信号
                signal_events = self.strategy.calculate_signals(mkt_event)

                # 信号 → 订单(经风控)
                for signal in signal_events:
                    order = self.portfolio.naive_order_from_signal(
                        signal, self.portfolio.equity
                    )
                    if order and self.risk_manager.check_order(order, self.portfolio):
                        # 撮合
                        fill = self.execution_handler.execute_order(order, mkt_event)
                        if fill:
                            self.portfolio.update_fill(fill)
                            self.analyzer.record_fill(fill)

                # 每日记录净值(以最后一只标的为准)
                if mkt_event == market_events[-1]:
                    self.analyzer.record_equity(
                        mkt_event.timestamp,
                        self.portfolio.equity
                    )

        # 输出报告
        return self.analyzer.performance_report()


# ============================================================
# Part 9: 完整测试 demo
# ============================================================

if __name__ == "__main__":
    import pandas as pd
    np.random.seed(42)

    # 模拟 2 只股票,1500 天
    symbols = ['STOCK_A', 'STOCK_B']
    n_days = 1500
    dates = pd.bdate_range('2020-01-01', periods=n_days)

    ohlcv_data = {}
    for sym in symbols:
        close = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, n_days)))
        ohlcv_data[sym] = pd.DataFrame({
            'open': close * (1 + np.random.uniform(-0.01, 0.01, n_days)),
            'high': close * (1 + np.abs(np.random.normal(0, 0.005, n_days))),
            'low': close * (1 - np.abs(np.random.normal(0, 0.005, n_days))),
            'close': close,
            'volume': np.random.randint(1_000_000, 5_000_000, n_days),
        }, index=dates)

    # 装配引擎
    data_handler = DataHandler(symbols, ohlcv_data)
    strategy = Strategy(symbols, fast_window=10, slow_window=30)
    portfolio = Portfolio(initial_capital=1_000_000, max_position_pct=0.1)
    risk_manager = RiskManager(max_order_value=200_000)
    execution_handler = ExecutionHandler(
        commission_rate=0.0003,    # 万三
        stamp_duty=0.001,          # 千一
        slippage_pct=0.0005        # 5 个 bp
    )
    analyzer = Analyzer()

    engine = BacktestingEngine(
        data_handler=data_handler,
        strategy=strategy,
        portfolio=portfolio,
        risk_manager=risk_manager,
        execution_handler=execution_handler,
        analyzer=analyzer,
    )

    # 跑回测
    report = engine.run()
    print("=" * 60)
    print("事件驱动回测报告")
    print("=" * 60)
    for k, v in report.items():
        print(f"  {k:<20}: {v}")
