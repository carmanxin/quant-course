# @quantlab/output: 8ab1f2e2
class TransactionCostModel:
    """
    完整的A股交易成本模型
    """
    def __init__(self,
                 commission_rate=0.0003,   # 佣金万三
                 stamp_tax_rate=0.0005,    # 印花税千0.5（仅卖出）
                 transfer_fee_rate=0.00002,  # 过户费万0.2
                 min_commission=5.0):       # 最低佣金5元
        self.commission_rate = commission_rate
        self.stamp_tax_rate = stamp_tax_rate
        self.transfer_fee_rate = transfer_fee_rate
        self.min_commission = min_commission

    def calculate_cost(self, price, shares, side, avg_daily_volume=None):
        """
        计算单笔交易的总成本

        Parameters:
            price: 成交均价
            shares: 成交股数（正数）
            side: 'buy' 或 'sell'
            avg_daily_volume: 日均成交量（股），用于估算冲击成本
        """
        value = price * shares

        # 显性成本
        commission = max(value * self.commission_rate, self.min_commission)
        stamp_tax = value * self.stamp_tax_rate if side == 'sell' else 0
        transfer_fee = max(value * self.transfer_fee_rate, 1.0)

        # 隐性成本：买卖价差（假设万二）
        spread_cost = value * 0.0002

        # 隐性成本：冲击成本（简化模型）
        if avg_daily_volume and avg_daily_volume > 0:
            participation_rate = shares / avg_daily_volume
            # 参与率越高，冲击成本越大
            impact_cost = value * (0.1 * np.sqrt(participation_rate))
        else:
            impact_cost = 0

        total_cost = commission + stamp_tax + transfer_fee + spread_cost + impact_cost

        return {
            'commission': commission,
            'stamp_tax': stamp_tax,
            'transfer_fee': transfer_fee,
            'spread_cost': spread_cost,
            'impact_cost': impact_cost,
            'total_cost': total_cost,
            'cost_rate': total_cost / value
        }
