# @quantlab/output: c18b56c9
import matplotlib.pyplot as plt
import numpy as np

# 5 个评估维度
categories = ['数学', '编程', '金融', '沟通', '工程化']
N = len(categories)

# 各岗位在 5 个维度的评分 (1-10)
roles = {
    'Quant Researcher':   [9, 7, 8, 6, 5],
    'Quant Developer':    [6, 9, 5, 5, 9],
    'Quant Trader':       [6, 7, 7, 6, 6],
    'Portfolio Manager':  [7, 6, 9, 9, 6],
    'Data Engineer':      [5, 9, 4, 5, 9],
    'Risk Manager':       [8, 6, 9, 7, 7],
    'ML/AI Engineer':     [9, 9, 5, 5, 8],
}

# 计算每个角色的角度
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]  # 闭合

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# 颜色配置
colors = ['#FF0080', '#7C3AED', '#00D4FF', '#00E5A0',
          '#FFB800', '#FF4D6D', '#94A3B8']

for idx, (role, values) in enumerate(roles.items()):
    values_closed = values + values[:1]
    ax.plot(angles, values_closed, linewidth=2.2,
            label=role, color=colors[idx])
    ax.fill(angles, values_closed, alpha=0.08, color=colors[idx])

# 设置雷达图样式
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9, color='gray')
ax.grid(True, alpha=0.4)
ax.spines['polar'].set_alpha(0.3)

ax.set_title('量化岗位能力雷达图 (2025-2026)\n'
             '5 维度评分模型:数学 25% + 编程 20% + 金融 20% + 沟通 15% + 工程化 20%',
             fontsize=14, fontweight='bold', pad=30)

# 图例放在右侧
ax.legend(loc='center left', bbox_to_anchor=(1.15, 0.5),
          fontsize=10, frameon=True)

plt.tight_layout()
plt.show()
