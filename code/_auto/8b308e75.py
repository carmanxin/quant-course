# @quantlab/output: 8b308e75
from dataclasses import dataclass


@dataclass
class Quote:
    bid: float
    ask: float
    fair: float


def inventory_aware_quote(
    fair: float,
    uncertainty: float,
    inventory: int,
    risk_penalty: float = 0.02,
    fee: float = 0.01,
) -> Quote:
    """面试用最小报价模型，不代表生产交易参数。"""
    shifted_fair = fair - risk_penalty * inventory
    half_spread = max(fee, 0.5 * uncertainty + fee)
    return Quote(
        bid=round(shifted_fair - half_spread, 2),
        ask=round(shifted_fair + half_spread, 2),
        fair=round(shifted_fair, 2),
    )


print("库存对报价的影响（fair=100.00, uncertainty=0.20, fee=0.01）")
print(f"{'库存':>6}{'bid':>9}{'ask':>9}{'中价':>9}{'相对 100 的偏移':>18}")
print("-" * 52)
for inv in (-20, -8, 0, 8, 20):
    q = inventory_aware_quote(fair=100.0, uncertainty=0.20, inventory=inv)
    print(f"{inv:>6}{q.bid:>9.2f}{q.ask:>9.2f}{q.fair:>9.2f}{q.fair - 100.0:>+18.2f}")

print("\n不确定性对半价差的影响（inventory=0）")
print(f"{'uncertainty':>12}{'bid':>9}{'ask':>9}{'价差':>8}")
print("-" * 40)
for u in (0.0, 0.05, 0.20, 0.60):
    q = inventory_aware_quote(fair=100.0, uncertainty=u, inventory=0)
    print(f"{u:>12.2f}{q.bid:>9.2f}{q.ask:>9.2f}{q.ask - q.bid:>8.2f}")

q = inventory_aware_quote(fair=100.0, uncertainty=0.20, inventory=8)
print(f"\n多头 8 手时: {q}")
print("解读：库存为正（手上有多头）→ 中价下移，卖出更积极、买入更保守，引导库存回到 0；")
print("      价差 = 2×max(fee, 0.5·uncertainty + fee)，不确定性越高价差越宽，且永远不低于手续费。")
