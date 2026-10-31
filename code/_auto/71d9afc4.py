# @quantlab/output: 71d9afc4
import time

def monitor_option_position():
    """监控一个期权组合的 GREEKS 变化"""
    # 假设持仓: 100 张 ATM Call + 50 张 ATM Put
    holdings = [("call", 100, 2.800), ("put", 50, 2.800)]
    S = 2.800
    T = 30 / 365
    r = 0.025

    total = {"delta": 0, "gamma": 0, "vega": 0, "theta": 0}

    for otype, qty, K in holdings:
        d, g, v, t = bs_greeks(S, K, T, r, sigma=0.20, otype=otype)
        total["delta"] += qty * d
        total["gamma"] += qty * g
        total["vega"] += qty * v
        total["theta"] += qty * t

    print("持仓 GREEKS 总览:")
    for k, v in total.items():
        print(f"  {k:<6}: {v:+.2f}")
    print()
    print("解读:")
    print(f"  • 当 50ETF 上涨 1 分钱,组合价值变动 {total['delta']*0.01:+.2f} 元/张, 即 100 份 {total['delta']*0.01*10000:+.2f} 元")
    print(f"  • 当隐含波动率上行 1%,组合价值变动 {total['vega']*100:+.2f} 元/张")
    print(f"  • 时间每过一天,组合 Theta = {total['theta']:+.2f} 元/张")

monitor_option_position()
