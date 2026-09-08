# @quantlab/output: b4898d09
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


print(inventory_aware_quote(fair=100.0, uncertainty=0.20, inventory=8))
