# @quantlab/output: 8cf49de4
fair_price = (bid + ask) / 2
inventory = current_position
spread = base_spread + inventory_skew * inventory
bid_quote = fair_price - spread / 2
ask_quote = fair_price + spread / 2
