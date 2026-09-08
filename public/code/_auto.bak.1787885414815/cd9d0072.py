# @quantlab/output: cd9d0072
import matplotlib.pyplot as plt
import numpy as np

# 2024-2026 头部机构 JD 关键词频次(百分比)
keywords = ['Python', 'Machine Learning', 'Statistics', 'C++ / Rust',
            'Time Series', 'Alpha / Factor', 'Backtest', 'Data Pipeline',
            'Deep Learning', 'Risk Mgmt', 'LLM / Agent', 'SQL']
freq_2024 = [88, 65, 68, 60, 55, 56, 50, 45, 32, 35, 5, 35]
freq_2026 = [92, 75, 70, 65, 60, 58, 55, 48, 42, 38, 28, 42]

x = np.arange(len(keywords))
width = 0.38

fig, ax = plt.subplots(figsize=(13, 6))
bars1 = ax.bar(x - width/2, freq_2024, width, label='2024',
               color='#94A3B8', edgecolor='white', linewidth=1.5)
bars2 = ax.bar(x + width/2, freq_2026, width, label='2026',
               color='#00E5A0', edgecolor='white', linewidth=1.5)

# 在柱子上方标数值
for bar in bars1 + bars2:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 1,
            f'{int(h)}%', ha='center', fontsize=8, fontweight='bold')

ax.set_ylabel('出现频率 (%)', fontsize=11, fontweight='bold')
ax.set_title('2024 vs 2026 头部量化机构 JD 关键词频次变化\n'
             '(数据来源:Citadel / Millennium / Jane Street / 幻方 / 九坤 / 明汯 等 10 家)',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(keywords, rotation=30, ha='right', fontsize=10)
ax.legend(fontsize=11, loc='upper right')
ax.grid(True, axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(0, 105)

plt.tight_layout()
plt.show()
