# @quantlab/output: c03d7ccb
import matplotlib.pyplot as plt
import numpy as np

# 数据准备:2025 年末/2026 年 Q1 估算 AUM (单位:亿美元)
firms = ['Citadel', 'Millennium', 'Bridgewater', 'Point72',
         'AQR', 'Two Sigma', 'D.E. Shaw', 'Jane Street',
         'MAN Group', 'Winton', 'Optiver', 'Renaissance(外部)']
aum = [630, 600, 580, 370, 320, 300, 270, 200, 180, 110, 100, 130]

# 按 AUM 降序排列
sorted_idx = np.argsort(aum)[::-1]
firms_sorted = [firms[i] for i in sorted_idx]
aum_sorted = [aum[i] for i in sorted_idx]

# 配色:头部三家用渐变突出
colors = ['#FF0080', '#7C3AED', '#00D4FF'] + ['#94A3B8'] * (len(firms) - 3)

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(firms_sorted, aum_sorted, color=colors, edgecolor='white', linewidth=1.5)

# 数值标签
for bar, val in zip(bars, aum_sorted):
    ax.text(val + 8, bar.get_y() + bar.get_height()/2,
            f'${val}B', va='center', fontsize=11, fontweight='bold')

ax.set_xlabel('AUM (亿美元)', fontsize=12, fontweight='bold')
ax.set_title('全球量化私募 AUM 排行 2025-2026\n(数据来源:13F/Form ADV/PivotalPath 估算)',
             fontsize=14, fontweight='bold', pad=15)
ax.invert_yaxis()
ax.grid(True, axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()
