# @quantlab/output: f2cc4dcb
import matplotlib.pyplot as plt
import numpy as np

# 时间序列(2020-2026 估算)
years = ['2020', '2022', '2024', '2025H1', '2025H2', '2026Q1']
total_aum = [800, 14000, 14500, 14800, 15500, 18000]  # 亿元
hedge_cost = [10, 18, 15, 16, 7, 8]  # 中性策略年化对冲成本中枢(%)
big_firms = [8, 25, 40, 50, 60, 60]  # 百亿量化私募家数

fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# 子图 1:AUM 增长曲线
ax = axes[0]
ax.plot(years, total_aum, marker='o', linewidth=2.5, color='#00E5A0', markersize=10)
ax.fill_between(years, total_aum, alpha=0.15, color='#00E5A0')
for x, y in zip(years, total_aum):
    ax.annotate(f'{y:,}', (x, y), textcoords="offset points",
                xytext=(0, 12), ha='center', fontsize=10, fontweight='bold')
ax.set_ylabel('AUM (亿元)', fontsize=11, fontweight='bold')
ax.set_title('中国量化私募总规模演变 (2020-2026)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 子图 2:对冲成本 vs 百亿机构数
ax = axes[1]
ax2 = ax.twinx()
bars = ax.bar(years, hedge_cost, alpha=0.6, color='#7C3AED', label='对冲成本(%)', width=0.6)
line = ax2.plot(years, big_firms, marker='s', linewidth=2.5,
                color='#FF0080', markersize=10, label='百亿机构数')
ax.set_ylabel('中性策略年化对冲成本 (%)', fontsize=11, fontweight='bold', color='#7C3AED')
ax2.set_ylabel('百亿量化私募数量', fontsize=11, fontweight='bold', color='#FF0080')
ax.set_title('对冲成本 vs 头部机构数', fontsize=12, fontweight='bold')
ax.tick_params(axis='y', labelcolor='#7C3AED')
ax2.tick_params(axis='y', labelcolor='#FF0080')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()
