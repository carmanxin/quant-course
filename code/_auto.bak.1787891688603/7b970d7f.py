# @quantlab/output: 7b970d7f
import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from collections import deque
import threading
from kafka import KafkaProducer, KafkaConsumer
import numpy as np

# ==================== 核心数据结构 ====================

@dataclass
class MarketTick:
    """行情Tick数据结构"""
    symbol: str
    timestamp: float
    bid_price: float
    ask_price: float
    bid_size: int
    ask_size: int
    last_price: float
    volume: int

@dataclass
class OrderRequest:
    """订单请求"""
    symbol: str
    side: str  # BUY / SELL
    order_type: str  # MKT / LMT
    price: float = 0.0
    quantity: int = 0
    order_id: str = ""

@dataclass
class OrderAck:
    """订单回执"""
    order_id: str
    status: str  # FILLED / PARTIAL / REJECTED / CANCELLED
    filled_qty: int = 0
    avg_price: float = 0.0
    message: str = ""

@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int = 0
    avg_cost: float = 0.0

    @property
    def market_value(self, current_price):
        return self.quantity * current_price

    @property
    def unrealized_pnl(self, current_price):
        return self.quantity * (current_price - self.avg_cost)

# ==================== 策略基类 ====================

class BaseStrategy(ABC):
    """量化策略基类"""

    def __init__(self, name: str, symbols: List[str]):
        self.name = name
        self.symbols = symbols
        self.positions: Dict[str, Position] = {
            s: Position(symbol=s) for s in symbols
        }
        self.market_data: Dict[str, deque] = {
            s: deque(maxlen=500) for s in symbols
        }
        self.realized_pnl = 0.0
        self.logger = logging.getLogger(f"strategy.{name}")

    @abstractmethod
    def on_tick(self, tick: MarketTick) -> Optional[OrderRequest]:
        """处理行情Tick，返回可选的订单请求"""
        pass

    def on_order_ack(self, ack: OrderAck):
        """处理订单回执"""
        pass

    @abstractmethod
    def compute_signal(self, symbol: str) -> float:
        """计算交易信号 (-1到1之间，正数看多，负数看空)"""
        pass

    def get_position(self, symbol: str) -> Position:
        return self.positions[symbol]

# ==================== 主引擎 ====================

class TradingEngine:
    """量化交易主引擎"""

    def __init__(self, broker_api=None, risk_manager=None):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.broker = broker_api
        self.risk_manager = risk_manager
        self.is_running = False

        # Kafka连接
        self.market_data_consumer = None
        self.order_producer = None

        # 性能统计
        self.tick_count = 0
        self.latency_stats: deque = deque(maxlen=1000)

        # 日志
        self.logger = logging.getLogger("engine")

    def register_strategy(self, strategy: BaseStrategy):
        """注册策略"""
        self.strategies[strategy.name] = strategy
        self.logger.info(f"注册策略: {strategy.name} (标的: {strategy.symbols})")

    def start(self):
        """启动引擎"""
        self.is_running = True
        self.logger.info("交易引擎启动")

        # 启动行情消费线程
        tick_thread = threading.Thread(target=self._consume_ticks, daemon=True)
        tick_thread.start()

        # 启动主循环
        self._main_loop()

    def _consume_ticks(self):
        """从Kafka消费行情"""
        # 实际应用中使用 KafkaConsumer
        self.logger.info("行情消费线程启动")

    def _main_loop(self):
        """主循环"""
        while self.is_running:
            try:
                # 1. 处理行情 → 信号
                # 2. 信号 → 订单
                # 3. 订单 → 风控检查
                # 4. 通过风控 → 发送到券商
                # 5. 处理回执 → 更新持仓/PnL
                # 6. 风险指标监控
                time.sleep(0.001)  # 1ms循环周期
            except KeyboardInterrupt:
                self.is_running = False
                self.logger.info("收到停止信号，正在关闭...")
            except Exception as e:
                self.logger.error(f"引擎异常: {e}", exc_info=True)

    def stop(self):
        """停止引擎"""
        self.is_running = False
        self.logger.info("交易引擎停止")

    def get_status(self) -> dict:
        """获取引擎状态摘要"""
        total_pnl = sum(
            s.realized_pnl for s in self.strategies.values()
        )
        return {
            'running': self.is_running,
            'n_strategies': len(self.strategies),
            'n_ticks_processed': self.tick_count,
            'total_realized_pnl': total_pnl,
            'avg_latency_ms': np.mean(self.latency_stats) * 1000 if self.latency_stats else 0,
        }

# ==================== 风险管理器 ====================

class RiskManager:
    """风险管理器"""

    def __init__(self, max_position_value=1e6, max_daily_loss=50000,
                 max_order_size=100000, max_cancel_rate=0.3):
        self.max_position_value = max_position_value
        self.max_daily_loss = max_daily_loss
        self.max_order_size = max_order_size
        self.max_cancel_rate = max_cancel_rate

        self.daily_pnl = 0.0
        self.order_history: deque = deque(maxlen=1000)
        self.cancel_history: deque = deque(maxlen=1000)

    def check_order(self, order: OrderRequest, positions: Dict[str, Position],
                    current_prices: Dict[str, float]) -> bool:
        """检查订单是否通过风控"""

        # 检查1: 日内亏损限制
        if self.daily_pnl < -self.max_daily_loss:
            self._log_reject(order, "日内亏损超限")
            return False

        # 检查2: 单笔订单规模
        if order.quantity * current_prices.get(order.symbol, 0) > self.max_order_size:
            self._log_reject(order, "订单规模超限")
            return False

        # 检查3: 持仓市值限制
        pos = positions.get(order.symbol)
        if pos:
            new_qty = pos.quantity + (order.quantity if order.side == 'BUY' else -order.quantity)
            new_value = abs(new_qty * current_prices.get(order.symbol, 0))
            if new_value > self.max_position_value:
                self._log_reject(order, "持仓市值超限")
                return False

        # 检查4: 撤单率
        if len(self.order_history) > 50:
            cancel_rate = len(self.cancel_history) / max(len(self.order_history), 1)
            if cancel_rate > self.max_cancel_rate:
                self._log_reject(order, f"撤单率过高 ({cancel_rate:.1%})")
                return False

        return True

    def _log_reject(self, order, reason):
        logging.warning(f"风控拒绝订单 [{order.symbol} {order.side} {order.quantity}]: {reason}")

    def update_pnl(self, pnl_change):
        self.daily_pnl += pnl_change

    def reset_daily(self):
        self.daily_pnl = 0.0
        self.order_history.clear()
        self.cancel_history.clear()

# ==================== 使用示例 ====================

class SimpleMomentumStrategy(BaseStrategy):
    """简单动量策略示例"""

    def __init__(self, name, symbols, lookback=20):
        super().__init__(name, symbols)
        self.lookback = lookback

    def on_tick(self, tick: MarketTick) -> Optional[OrderRequest]:
        self.market_data[tick.symbol].append(tick)

        if len(self.market_data[tick.symbol]) < self.lookback:
            return None

        signal = self.compute_signal(tick.symbol)

        current_pos = self.positions[tick.symbol]

        # 简单逻辑: 信号>0.3买入，信号<-0.3卖出
        target_qty = 0
        if signal > 0.3:
            target_qty = 100
        elif signal < -0.3:
            target_qty = -100

        # 计算需要交易的量
        delta = target_qty - current_pos.quantity
        if delta == 0:
            return None

        side = 'BUY' if delta > 0 else 'SELL'
        return OrderRequest(
            symbol=tick.symbol,
            side=side,
            order_type='MKT',
            quantity=abs(delta)
        )

    def compute_signal(self, symbol: str) -> float:
        data = list(self.market_data[symbol])
        prices = np.array([t.last_price for t in data])

        # 简单动量: (当前价 - N期前价格) / N期前价格
        momentum = (prices[-1] - prices[0]) / prices[0]

        # 归一化到[-1, 1]
        return np.clip(momentum * 10, -1, 1)

# 创建和启动引擎
engine = TradingEngine()
risk_mgr = RiskManager(max_position_value=500000, max_daily_loss=20000)
engine.risk_manager = risk_mgr

strategy = SimpleMomentumStrategy('momentum_1', ['AAPL', 'GOOGL', 'MSFT'])
engine.register_strategy(strategy)

print("量化交易引擎架构演示已就绪")
print(f"  注册策略数: {len(engine.strategies)}")
print(f"  风控参数: 最大持仓={risk_mgr.max_position_value}, 日内最大亏损={risk_mgr.max_daily_loss}")
