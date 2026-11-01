# @quantlab/output: 67486ab5
arrival_price = 100
executed_price = 100.3
shortfall = (executed_price - arrival_price) / arrival_price
print(f"执行缺口: {shortfall:.3%}")
