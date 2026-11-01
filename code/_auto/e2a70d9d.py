# @quantlab/output: e2a70d9d
if order_size > market_depth * 0.5:
    send_to_dark_pool(order)
else:
    send_to_lit_market(order)
