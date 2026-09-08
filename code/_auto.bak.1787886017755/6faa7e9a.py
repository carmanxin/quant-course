# @quantlab/output: 6faa7e9a
# Pyodide 沙箱已自动注入 demo 数据集(nav_no_cost / trades / capital 等),
# 直接点击 ▶ 一键运行即可看到成本侵蚀效果。
cost_rate = 0.001
nav_with_cost = nav_no_cost.copy()
for i in range(1, len(nav_with_cost)):
    if trades[i] != 0:
        nav_with_cost[i:] *= (1 - cost_rate)

# 比较有无成本的最终净值
final_no_cost    = nav_no_cost[-1]
final_with_cost  = nav_with_cost[-1]
total_drag_pct   = (final_with_cost - final_no_cost) / final_no_cost * 100
print(f'无成本终值: ${final_no_cost:,.0f}')
print(f'有成本终值: ${final_with_cost:,.0f}')
print(f'总成本侵蚀: {total_drag_pct:.2f}%')
