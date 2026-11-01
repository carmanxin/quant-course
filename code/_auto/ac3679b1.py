# @quantlab/output: ac3679b1
import numpy as np

def inventory_skew_analysis(fair_price, base_spread, positions, skew_coeff):
    """
    分析库存偏斜对报价的影响

    返回每个持仓水平下的买单偏移、卖单偏移
    """
    results = []
    for pos in positions:
        # 买价：从中间价减去半价差，再加库存偏斜
        bid_offset = -(base_spread / 2) + skew_coeff * pos
        # 卖价：从中间价加上半价差，再加库存偏斜
        ask_offset = (base_spread / 2) + skew_coeff * pos

        bid_price = fair_price + bid_offset
        ask_price = fair_price + ask_offset
        effective_spread = ask_price - bid_price

        results.append({
            'position': pos,
            'bid_price': bid_price,
            'ask_price': ask_price,
            'spread': effective_spread,
            'skewed': pos != 0
        })
    return results

# 分析不同持仓水平下的报价偏斜
fair = 100.0
base_spr = 0.10
skew_coeff = 0.005

positions = [-200, -100, -50, 0, 50, 100, 200]
results = inventory_skew_analysis(fair, base_spr, positions, skew_coeff)

print("库存偏斜分析（基准价差 = 0.10）:")
print(f"{'持仓':>6} {'买价':>8} {'卖价':>8} {'价差':>8} {'报价方向':>12}")
print("-" * 50)
for r in results:
    skew_dir = ""
    if r['position'] > 0:
        skew_dir = "偏好卖出"
    elif r['position'] < 0:
        skew_dir = "偏好买入"
    else:
        skew_dir = "中性"
    print(f"{r['position']:>6} {r['bid_price']:>8.3f} {r['ask_price']:>8.3f} "
          f"{r['spread']:>8.3f} {skew_dir:>12}")
