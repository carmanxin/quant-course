# @quantlab/output: 44224404
imbalance = (buy_volume - sell_volume) / (buy_volume + sell_volume)
if imbalance > threshold:
    place_order('buy')
