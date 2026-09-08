# @quantlab/output: 05656c14
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import threading
import time
import logging

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    MARKET = "MKT"
    LIMIT = "LMT"
    STOP = "STP"
    STOP_LIMIT = "STP_LMT"

class OrderStatus(Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class Order:
    """标准订单结构"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    limit_price: float = 0.0
    stop_price: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    filled_qty: int = 0
    avg_fill_price: float = 0.0
    timestamp: float = 0.0

@dataclass
class AccountInfo:
    """账户信息"""
    account_id: str
    buying_power: float
    total_cash: float
    net_liquidation: float
    unrealized_pnl: float
    realized_pnl: float

@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int
    avg_cost: float
    market_price: float
    market_value: float
    unrealized_pnl: float

class BrokerAPI(ABC):
    """券商API抽象基类"""

    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.order_callbacks: List[Callable] = []
        self.trade_callbacks: List[Callable] = []
        self.logger = logging.getLogger(f"broker.{name}")

    # ---- 连接管理 ----

    @abstractmethod
    def connect(self, host: str, port: int, **kwargs) -> bool:
        """连接到券商服务器"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass

    # ---- 账户查询 ----

    @abstractmethod
    def get_account_info(self) -> Optional[AccountInfo]:
        """获取账户信息"""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """获取当前持仓列表"""
        pass

    # ---- 订单操作 ----

    @abstractmethod
    def place_order(self, order: Order) -> str:
        """下单，返回订单ID"""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        pass

    @abstractmethod
    def cancel_all_orders(self, symbol: str = None) -> int:
        """取消所有（或某标的的）未成交订单"""
        pass

    @abstractmethod
    def get_open_orders(self) -> List[Order]:
        """获取所有未成交订单"""
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Optional[Order]:
        """查询订单状态"""
        pass

    # ---- 回调注册 ----

    def on_order_update(self, callback: Callable):
        """注册订单状态更新回调"""
        self.order_callbacks.append(callback)

    def on_trade(self, callback: Callable):
        """注册成交回报回调"""
        self.trade_callbacks.append(callback)

    def _notify_order_update(self, order: Order):
        for cb in self.order_callbacks:
            try:
                cb(order)
            except Exception:
                pass

    def _notify_trade(self, order: Order):
        for cb in self.trade_callbacks:
            try:
                cb(order)
            except Exception:
                pass

# ==================== 模拟券商实现 ====================

class SimulatedBroker(BrokerAPI):
    """模拟券商 - 用于Paper Trading"""

    def __init__(self, name="SimBroker", initial_cash=1000000.0):
        super().__init__(name)
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.order_counter = 0
        self.filled_orders: List[Order] = []

        # 模拟成交线程
        self._running = False
        self._match_thread = None

    def connect(self, host='', port=0, **kwargs):
        self.is_connected = True
        self._running = True
        self._match_thread = threading.Thread(target=self._matching_loop, daemon=True)
        self._match_thread.start()
        self.logger.info(f"模拟券商连接成功 (初始资金: {self.cash:,.0f})")
        return True

    def disconnect(self):
        self._running = False
        self.is_connected = False
        self.logger.info("模拟券商断开")
        return True

    def _matching_loop(self):
        """模拟订单匹配循环"""
        while self._running:
            for order_id, order in list(self.orders.items()):
                if order.status in (OrderStatus.PENDING, OrderStatus.SUBMITTED):
                    # 模拟：80%概率成交，市价单100%成交
                    fill_prob = 1.0 if order.order_type == OrderType.MARKET else 0.8
                    if order_id in self.orders:  # 可能已被取消
                        if order.order_type == OrderType.MARKET:
                            self._fill_order(order_id, order.quantity)
                        else:
                            self._fill_order(order_id, order.quantity)
            time.sleep(1.0)

    def _fill_order(self, order_id: str, fill_qty: int):
        """模拟订单成交"""
        order = self.orders.get(order_id)
        if not order or order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED):
            return

        # 更新订单状态
        order.filled_qty = fill_qty
        order.status = OrderStatus.FILLED
        order.avg_fill_price = order.limit_price if order.limit_price > 0 else 100.0

        # 更新持仓和现金
        if order.symbol not in self.positions:
            self.positions[order.symbol] = Position(
                symbol=order.symbol, quantity=0, avg_cost=0,
                market_price=order.avg_fill_price, market_value=0, unrealized_pnl=0
            )

        pos = self.positions[order.symbol]
        fill_value = fill_qty * order.avg_fill_price

        if order.side == OrderSide.BUY:
            pos.quantity += fill_qty
            total_cost = pos.quantity * pos.avg_cost + fill_value
            pos.avg_cost = total_cost / pos.quantity if pos.quantity > 0 else 0
            self.cash -= fill_value
        else:
            pos.quantity -= fill_qty
            self.cash += fill_value

        self.filled_orders.append(order)
        self._notify_trade(order)

    def place_order(self, order: Order) -> str:
        order_id = f"SIM_{self.order_counter:06d}"
        self.order_counter += 1
        order.order_id = order_id
        order.status = OrderStatus.SUBMITTED
        order.timestamp = time.time()
        self.orders[order_id] = order
        self.logger.info(f"下单: {order.symbol} {order.side.value} {order.quantity} "
                        f"({order.order_type.value}) [ID: {order_id}]")
        return order_id

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status not in (OrderStatus.FILLED, OrderStatus.CANCELLED):
                order.status = OrderStatus.CANCELLED
                self.logger.info(f"撤单: {order_id}")
                return True
        return False

    def cancel_all_orders(self, symbol: str = None) -> int:
        count = 0
        for oid, order in list(self.orders.items()):
            if symbol is None or order.symbol == symbol:
                if self.cancel_order(oid):
                    count += 1
        return count

    def get_account_info(self) -> AccountInfo:
        total_market_value = sum(
            p.quantity * p.market_price for p in self.positions.values()
        )
        net_liq = self.cash + total_market_value
        return AccountInfo(
            account_id="SIM_ACCOUNT",
            buying_power=self.cash * 2,  # 模拟2倍杠杆
            total_cash=self.cash,
            net_liquidation=net_liq,
            unrealized_pnl=sum(p.unrealized_pnl for p in self.positions.values()),
            realized_pnl=0.0
        )

    def get_positions(self) -> List[Position]:
        return list(self.positions.values())

    def get_open_orders(self) -> List[Order]:
        return [o for o in self.orders.values()
                if o.status not in (OrderStatus.FILLED, OrderStatus.CANCELLED)]

    def get_order_status(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)

# ==================== 订单管理器 ====================

class OrderManager:
    """订单管理器：在策略逻辑和券商API之间建立缓冲层"""

    def __init__(self, broker: BrokerAPI):
        self.broker = broker
        self.pending_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []
        self.max_retries = 3

    def submit_order(self, order: Order) -> Optional[str]:
        """提交订单（含自动重试）"""
        for attempt in range(self.max_retries):
            try:
                order_id = self.broker.place_order(order)
                if order_id:
                    self.pending_orders[order_id] = order
                    return order_id
            except Exception as e:
                logging.error(f"下单失败 (尝试 {attempt+1}/{self.max_retries}): {e}")
                time.sleep(1.0)

        logging.error(f"订单提交彻底失败: {order.symbol} {order.side}")
        return None

    def reconcile(self) -> dict:
        """订单对账：确保本地记录与券商状态一致"""
        broker_orders = {}
        try:
            broker_orders = {
                o.order_id: o for o in self.broker.get_open_orders()
            }
        except Exception as e:
            logging.warning(f"获取券商订单失败: {e}")

        # 检查本地有但券商没有的订单
        for oid, local_order in list(self.pending_orders.items()):
            if oid not in broker_orders:
                # 订单可能已成交或已被取消
                self.order_history.append(local_order)
                del self.pending_orders[oid]

        return {
            'pending_count': len(self.pending_orders),
            'synced': len(broker_orders)
        }

# ==================== 使用示例 ====================

# 创建模拟券商进行Paper Trading
sim_broker = SimulatedBroker(initial_cash=500000)
sim_broker.connect()

order_mgr = OrderManager(sim_broker)

# 注册成交回调
def on_fill(order):
    print(f"  [成交] {order.symbol} {order.side.value} {order.filled_qty} @ {order.avg_fill_price:.2f}")

sim_broker.on_trade(on_fill)

# 发送订单
order1 = Order(
    order_id='', symbol='AAPL', side=OrderSide.BUY,
    order_type=OrderType.MARKET, quantity=100
)
order_mgr.submit_order(order1)

order2 = Order(
    order_id='', symbol='TSLA', side=OrderSide.SELL,
    order_type=OrderType.LIMIT, quantity=50, limit_price=250.0
)
order_mgr.submit_order(order2)

time.sleep(3)  # 等待成交

# 查看状态
acc_info = sim_broker.get_account_info()
positions = sim_broker.get_positions()

print(f"\n账户概览: 现金={acc_info.total_cash:,.0f}, 净值={acc_info.net_liquidation:,.0f}")
print(f"持仓数: {len(positions)}")
for pos in positions:
    print(f"  {pos.symbol}: {pos.quantity}股 @ {pos.avg_cost:.2f}")

sim_broker.disconnect()
