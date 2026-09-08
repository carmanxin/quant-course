# @quantlab/output: 08d1b078
class PreTradeCompliance:
    """盘前合规检查器 - 在每个订单发送前执行"""

    def __init__(self, position_limits, restricted_stocks,
                 max_order_value, min_price, max_price):
        self.position_limits = position_limits  # {symbol: max_shares}
        self.restricted_stocks = set(restricted_stocks)
        self.max_order_value = max_order_value
        self.min_price = min_price  # 最低允许价格
        self.max_price = max_price  # 最高允许价格

    def check(self, order: dict, current_positions: dict,
              current_price: float) -> tuple:
        """
        盘前合规检查

        返回: (passed: bool, reason: str)
        """
        symbol = order['symbol']
        qty = order['quantity']
        side = order['side']
        price = order.get('price', current_price)

        # 1. 禁买/禁卖名单检查
        if symbol in self.restricted_stocks:
            return False, f"{symbol} 在限制交易名单中"

        # 2. 价格合理性检查
        if price < self.min_price or price > self.max_price:
            return False, f"价格 {price} 超出合理范围 [{self.min_price}, {self.max_price}]"

        # 3. 订单价值检查
        order_value = abs(qty * price)
        if order_value > self.max_order_value:
            return False, f"订单价值 {order_value:,.0f} 超过单笔上限 {self.max_order_value:,.0f}"

        # 4. 持仓限制检查
        current_qty = current_positions.get(symbol, 0)
        new_qty = current_qty + (qty if side == 'BUY' else -qty)

        if symbol in self.position_limits:
            limit = self.position_limits[symbol]
            if abs(new_qty) > limit:
                return False, f"下单后持仓 {abs(new_qty)} 超过限额 {limit}"

        # 5. 空头检查（如果账户不允许卖空）
        if side == 'SELL' and current_qty < qty:
            return False, f"可卖数量不足（持仓: {current_qty}, 卖出: {qty}）"

        return True, "检查通过"

# 初始化盘前风控
pre_trade = PreTradeCompliance(
    position_limits={'AAPL': 5000, 'TSLA': 2000, 'NVDA': 3000},
    restricted_stocks={'GME', 'AMC'},  # 限制名单
    max_order_value=500000,
    min_price=1.0,
    max_price=5000.0
)

# 测试几个订单
test_orders = [
    {'symbol': 'AAPL', 'side': 'BUY', 'quantity': 1000, 'price': 150.0},
    {'symbol': 'GME', 'side': 'BUY', 'quantity': 100, 'price': 25.0},  # 限制名单
    {'symbol': 'TSLA', 'side': 'BUY', 'quantity': 3000, 'price': 250.0},  # 超限
    {'symbol': 'NVDA', 'side': 'SELL', 'quantity': 500, 'price': 800.0},
]

print("\nPre-Trade合规检查:")
for order in test_orders:
    passed, reason = pre_trade.check(
        order,
        current_positions={'AAPL': 2000, 'NVDA': 200},
        current_price=order['price']
    )
    status = "PASS" if passed else "REJECT"
    print(f"  [{status}] {order['symbol']} {order['side']} {order['quantity']}: {reason}")
