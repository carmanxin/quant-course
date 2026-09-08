# @quantlab/output: fbfca891
# 做市商库存风险管理示意
# 假设做市商在某个 ATM Call 上累计卖出 500 张
# 持仓 delta = -500 × 0.5 = -250 (空头 delta)
# 必须买入 25000 份 50ETF 现货来对冲
def hedger_holdings_to_hedge(shrt_call_qty=500, call_delta=0.5, S=2.800):
    """做市商对冲所需买入的现货数量"""
    required_hedge = -shrt_call_qty * call_delta * 10000
    notional = required_hedge * S
    print(f"  持仓空头 Call: {shrt_call_qty} 张, 每张 delta={call_delta}")
    print(f"  需买入现货对冲: {-required_hedge:,.0f} 份")
    print(f"  对冲名义金额: {notional:,.0f} 元")
    return -required_hedge

hedge_amount = hedger_holdings_to_hedge()
