# @quantlab/output: f13e2ae8
import numpy as np
from collections import deque

class MarketMaker:
    """基于Avellaneda-Stoikov模型的做市策略模拟器"""

    def __init__(self, initial_cash=1000000, initial_position=0,
                 base_spread=0.02, gamma=0.01, sigma=0.30,
                 max_position=1000, order_arrival_rate=10):
        self.cash = initial_cash
        self.position = initial_position
        self.base_spread = base_spread
        self.gamma = gamma          # 风险厌恶系数
        self.sigma = sigma          # 波动率估计
        self.max_position = max_position
        self.kappa = order_arrival_rate
        self.trades = []
        self.pnl_history = []

    def calculate_quotes(self, fair_price, remaining_time=1.0):
        """根据Avellaneda-Stoikov模型计算最优报价"""
        # 库存风险调整
        inventory_risk = self.gamma * self.sigma**2 * remaining_time * self.position**2

        # 基本价格偏移（从A-S模型推导的简化形式）
        reserve_price = fair_price - self.position * self.gamma * self.sigma**2 * remaining_time

        # 价差：基础价差 + 库存调整 + 风险调整
        spread = self.base_spread + self.gamma * self.sigma**2 * remaining_time * abs(self.position)
        # 保证价差不为负
        spread = max(spread, 0.005)

        # 仓位限制
        if abs(self.position) >= self.max_position:
            spread *= 2.0  # 接近仓位上限时大幅扩大价差

        bid_quote = reserve_price - spread / 2
        ask_quote = reserve_price + spread / 2

        return bid_quote, ask_quote, reserve_price

    def simulate_trade(self, trade_type, quantity, price):
        """模拟成交"""
        if trade_type == 'SELL':  # 对手方卖给我们（我们买入）
            self.position += quantity
            self.cash -= quantity * price
        elif trade_type == 'BUY':   # 对手方从我们这里买（我们卖出）
            self.position -= quantity
            self.cash += quantity * price
        self.trades.append({
            'type': trade_type, 'qty': quantity, 'price': price,
            'position': self.position, 'cash': self.cash
        })

    def calculate_pnl(self, current_price):
        """计算实时PnL（Mark-to-Market）"""
        return self.cash + self.position * current_price

# ===== 模拟做市过程 =====
np.random.seed(42)
market_maker = MarketMaker(initial_cash=1000000, base_spread=0.05,
                           gamma=0.005, sigma=0.25)

n_steps = 500
price = 100.0
prices = [price]

for t in range(n_steps):
    # 模拟价格随机游走
    price_change = np.random.normal(0, 0.1)
    price += price_change
    prices.append(price)

    fair_price = price
    remaining = 1.0 - t / n_steps

    bid_q, ask_q, reserve = market_maker.calculate_quotes(fair_price, remaining)

    # 模拟成交（简化：以一定概率在bid/ask价格成交）
    fill_prob = 0.3  # 每个时间步有30%概率在一边成交
    if np.random.random() < fill_prob and market_maker.position < market_maker.max_position:
        # 以bid价买入
        market_maker.simulate_trade('SELL', 10, bid_q)
    if np.random.random() < fill_prob and market_maker.position > -market_maker.max_position:
        # 以ask价卖出
        market_maker.simulate_trade('BUY', 10, ask_q)

    if t % 50 == 0:
        spread_bp = (ask_q - bid_q) * 10000 / fair_price
        pnl = market_maker.calculate_pnl(price)
        print(f"Step {t:3d}: 价格={price:.2f} 持仓={market_maker.position:4d} "
              f"价差={spread_bp:.1f}bp PnL={pnl:.0f}")

final_pnl = market_maker.calculate_pnl(price)
print(f"\n最终PnL: {final_pnl:.0f}  最终持仓: {market_maker.position}")
print(f"总成交笔数: {len(market_maker.trades)}")
