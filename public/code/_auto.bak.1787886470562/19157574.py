# @quantlab/output: 19157574
class ZeroIntelligenceLOB:
    """
    零智能限价订单簿模拟器。

    订单的到达、取消由 Poisson 过程驱动，订单价格和数量从指定分布中抽取。
    价格发现通过市价单匹配限价单实现。
    """

    def __init__(self,
                 initial_mid_price: float = 100.0,
                 tick_size: float = 0.01,
                 lambda_lo: float = 50.0,    # 限价单到达率
                 lambda_mo: float = 30.0,    # 市价单到达率
                 lambda_cancel: float = 20.0, # 取消率
                 price_jump_std: float = 0.05):
        self.mid_price = initial_mid_price
        self.tick_size = tick_size
        self.lambda_lo = lambda_lo
        self.lambda_mo = lambda_mo
        self.lambda_cancel = lambda_cancel
        self.price_jump_std = price_jump_std

        # 买卖订单簿：{price: quantity}
        self.bids = {}
        self.asks = {}
        self.time = 0.0
        self.trade_log = []
        self.mid_price_history = []

    def _generate_limit_price(self, side: str) -> float:
        """生成限价单价格"""
        n_ticks = int(np.random.exponential(5) + 1)
        offset = n_ticks * self.tick_size
        if side == 'bid':
            price = self.mid_price - offset
        else:
            price = self.mid_price + offset
        return round(price / self.tick_size) * self.tick_size

    def _generate_size(self) -> int:
        """生成订单量"""
        return int(np.random.exponential(500) + 100)

    def step(self) -> dict:
        """执行一个模拟步长（1秒）"""
        events = []

        # 1. 限价单到达
        n_lo = np.random.poisson(self.lambda_lo)
        for _ in range(n_lo):
            side = np.random.choice(['bid', 'ask'])
            price = self._generate_limit_price(side)
            size = self._generate_size()

            if side == 'bid':
                self.bids[price] = self.bids.get(price, 0) + size
            else:
                self.asks[price] = self.asks.get(price, 0) + size

            events.append({
                'type': 'limit_order',
                'side': side,
                'price': price,
                'size': size,
                'time': self.time
            })

        # 2. 市价单到达
        n_mo = np.random.poisson(self.lambda_mo)
        for _ in range(n_mo):
            side = np.random.choice(['buy', 'sell'])
            size = self._generate_size()

            remaining = size
            trade_price = None

            if side == 'buy':
                sorted_asks = sorted(self.asks.keys())
                for ask_price in sorted_asks:
                    available = self.asks[ask_price]
                    matched = min(remaining, available)
                    self.asks[ask_price] -= matched
                    if self.asks[ask_price] <= 0:
                        del self.asks[ask_price]
                    remaining -= matched
                    trade_price = ask_price
                    if remaining <= 0:
                        break
            else:
                sorted_bids = sorted(self.bids.keys(), reverse=True)
                for bid_price in sorted_bids:
                    available = self.bids[bid_price]
                    matched = min(remaining, available)
                    self.bids[bid_price] -= matched
                    if self.bids[bid_price] <= 0:
                        del self.bids[bid_price]
                    remaining -= matched
                    trade_price = bid_price
                    if remaining <= 0:
                        break

            if trade_price is not None:
                self.mid_price = trade_price
                self.trade_log.append({
                    'time': self.time,
                    'price': trade_price,
                    'volume': size - remaining,
                    'side': side
                })

            events.append({
                'type': 'market_order',
                'side': side,
                'price': trade_price,
                'size': size - remaining,
                'time': self.time
            })

        # 3. 随机取消
        n_cancel = np.random.poisson(self.lambda_cancel)
        for _ in range(n_cancel):
            side = np.random.choice(['bid', 'ask'])
            book = self.bids if side == 'bid' else self.asks
            if book:
                price = np.random.choice(list(book.keys()))
                cancel_size = min(
                    np.random.exponential(200),
                    book[price]
                )
                book[price] -= cancel_size
                if book[price] <= 0:
                    del book[price]

                events.append({
                    'type': 'cancel',
                    'side': side,
                    'price': price,
                    'size': cancel_size,
                    'time': self.time
                })

        # 4. 随机噪音（外生价格变动）
        self.mid_price += np.random.randn() * self.price_jump_std

        self.time += 1.0
        self.mid_price_history.append(self.mid_price)

        return events

    def get_best_prices(self) -> dict:
        """获取最佳买卖价"""
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        return {
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': (best_ask - best_bid) if (best_bid and best_ask) else None
        }

    def run(self, n_steps: int = 1000, verbose: bool = False) -> pd.DataFrame:
        """运行模拟器 n_steps 秒"""
        for step in range(n_steps):
            self.step()
            if verbose and step % 100 == 0:
                best = self.get_best_prices()
                print(f"Step {step}: Mid={self.mid_price:.2f}, "
                      f"Spread={best['spread']}")

        return pd.DataFrame(self.trade_log)
