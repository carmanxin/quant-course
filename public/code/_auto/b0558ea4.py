# @quantlab/output: b0558ea4
class LiquidationRiskManager:
    """
    永续合约爆仓风险管理器
    """

    def __init__(self, position_value, entry_price, leverage, maintenance_margin_rate=0.005):
        self.position_value = position_value
        self.entry_price = entry_price
        self.leverage = leverage
        self.maintenance_margin_rate = maintenance_margin_rate
        self.margin = position_value / leverage

    def liquidation_price(self, is_long=True):
        """
        计算强平价格
        """
        if is_long:
            liq_price = self.entry_price * (
                1 - (1 / self.leverage - self.maintenance_margin_rate)
            )
        else:
            liq_price = self.entry_price * (
                1 + (1 / self.leverage - self.maintenance_margin_rate)
            )
        return liq_price

    def margin_ratio(self, current_price, is_long=True):
        """
        计算当前保证金率
        """
        if is_long:
            unrealized_pnl = (current_price / self.entry_price - 1) * self.position_value
        else:
            unrealized_pnl = (1 - current_price / self.entry_price) * self.position_value

        current_equity = self.margin + unrealized_pnl
        margin_ratio = current_equity / self.position_value

        return {
            'margin_ratio': margin_ratio,
            'unrealized_pnl': unrealized_pnl,
            'current_equity': current_equity,
            'warning': margin_ratio < 0.05,
            'critical': margin_ratio < 0.02
        }

    def risk_budget_allocation(self, max_risk_per_trade_pct=0.02):
        """
        风险预算分配 —— 控制单笔交易的最大亏损
        """
        # 每笔交易的最大亏损额
        max_loss = self.margin * max_risk_per_trade_pct * 5  # 假设5倍初始风险

        # 对应止损价格
        if self.leverage > 0:
            stop_loss_pct = max_loss / (self.position_value * self.leverage)

        return {
            'max_loss_amount': max_loss,
            'stop_loss_pct_from_entry': stop_loss_pct * 100,
            'stop_loss_price': self.entry_price * (1 - stop_loss_pct),
            'risk_reward_required': 1 / max_risk_per_trade_pct  # 需要的最小盈亏比
        }
