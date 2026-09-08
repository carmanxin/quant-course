# @quantlab/output: 1699f4ac
class LOBBacktester:
    """
    基于订单簿回放的做市策略回测器。
    """

    def __init__(self, lob_data: pd.DataFrame):
        """
        参数:
            lob_data: LOB快照数据，包含时间戳和各级买卖价量
        """
        self.lob_data = lob_data.sort_values('timestamp').reset_index(drop=True)
        self.position = 0
        self.cash = 0.0
        self.active_orders = {'bid': [], 'ask': []}  # [(price, size, timestamp)]
        self.fill_log = []
        self.pnl = []

    def _check_fills(self, current_idx: int) -> list:
        """检查当前快照下是否有订单成交"""
        current = self.lob_data.iloc[current_idx]
        best_bid = current['bid_price_1']
        best_ask = current['ask_price_1']
        best_bid_size = current['bid_size_1']
        best_ask_size = current['ask_size_1']

        fills = []

        # 检查卖单成交（挂的卖单被买方吃掉）
        for i, (price, size, ts) in enumerate(self.active_orders['ask']):
            if price <= best_bid:  # 卖价低于等于最优买价，成交
                fill_prob = min(1.0, best_bid_size / size)
                if np.random.random() < fill_prob:
                    fills.append({
                        'side': 'sell',
                        'price': price,
                        'size': size,
                        'time': current['timestamp']
                    })
                    self.position -= size
                    self.cash += price * size
                    self.active_orders['ask'].pop(i)

        # 检查买单成交
        for i, (price, size, ts) in enumerate(self.active_orders['bid']):
            if price >= best_ask:
                fill_prob = min(1.0, best_ask_size / size)
                if np.random.random() < fill_prob:
                    fills.append({
                        'side': 'buy',
                        'price': price,
                        'size': size,
                        'time': current['timestamp']
                    })
                    self.position += size
                    self.cash -= price * size
                    self.active_orders['bid'].pop(i)

        return fills

    def _cancel_stale_orders(self, current_time, max_age_seconds: float = 5.0):
        """取消超时未成交的挂单"""
        for side in ['bid', 'ask']:
            self.active_orders[side] = [
                (p, s, ts) for p, s, ts in self.active_orders[side]
                if (current_time - ts).total_seconds() < max_age_seconds
            ]

    def run(self,
            quote_func,
            max_position: int = 1000,
            order_size: int = 100,
            cancel_age: float = 5.0) -> pd.DataFrame:
        """
        执行回测。

        参数:
            quote_func: 报价函数，接收 (current_idx, position, lob_data) 返回
                       {'bid_price': float, 'ask_price': float, 'bid_size': int,
                        'ask_size': int}
        """
        for i in range(len(self.lob_data)):
            current_time = self.lob_data.iloc[i]['timestamp']

            # 1. 检查成交
            fills = self._check_fills(i)
            self.fill_log.extend(fills)

            # 2. 取消过期订单
            self._cancel_stale_orders(current_time, cancel_age)

            # 3. 生成新报价
            if abs(self.position) < max_position:
                quotes = quote_func(i, self.position, self.lob_data)
                if quotes:
                    bid_p = quotes.get('bid_price')
                    ask_p = quotes.get('ask_price')
                    bid_s = quotes.get('bid_size', order_size)
                    ask_s = quotes.get('ask_size', order_size)

                    if bid_p is not None:
                        self.active_orders['bid'].append(
                            (bid_p, bid_s, current_time)
                        )
                    if ask_p is not None:
                        self.active_orders['ask'].append(
                            (ask_p, ask_s, current_time)
                        )

            # 4. 记录市值盈亏
            mid = (self.lob_data.iloc[i]['bid_price_1'] +
                   self.lob_data.iloc[i]['ask_price_1']) / 2
            mtm = self.cash + self.position * mid
            self.pnl.append({
                'time': current_time,
                'position': self.position,
                'cash': self.cash,
                'mtm': mtm
            })

        return pd.DataFrame(self.pnl)
