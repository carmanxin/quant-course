# @quantlab/output: e4c5589a
import matplotlib.pyplot as plt
import numpy as np

# 5 大误区的"杀伤力"(满分 10)
pitfalls = {
    '过度拟合':     {'kill': 9.5, 'freq': 9.0, 'detect': 5.0},
    '幸存者偏差':   {'kill': 8.0, 'freq': 6.5, 'detect': 4.5},
    '忽视交易成本': {'kill': 7.5, 'freq': 8.5, 'detect': 7.0},
    '策略拥挤':     {'kill': 8.5, 'freq': 9.5, 'detect': 6.0},
    '数据泄漏':     {'kill': 9.5, 'freq': 7.0, 'detect': 3.0},
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 子图 1:杀伤力 vs 频率 散点图(气泡大小=难以检测度)
ax = axes[0]
for idx, (name, p) in enumerate(pitfalls.items()):
    size = 200 + (10 - p['detect']) * 80  # 越难检测越大
    color = ['#FF0080', '#7C3AED', '#00D4FF', '#FFB800', '#FF4D6D'][idx]
    ax.scatter(p['freq'], p['kill'], s=size, color=color,
               alpha=0.7, edgecolor='white', linewidth=2)
    ax.annotate(name, (p['freq'], p['kill']),
                xytext=(8, 8), textcoords='offset points',
                fontsize=11, fontweight='bold')

ax.set_xlabel('出现频率 (1-10)', fontsize=11, fontweight='bold')
ax.set_ylabel('杀伤力 (1-10)', fontsize=11, fontweight='bold')
ax.set_title('5 大误区的杀伤力 vs 出现频率\n(气泡越大=越难检测)',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(4, 11)
ax.set_ylim(6, 11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 子图 2:雷达图:杀伤力 / 频率 / 检测难度
categories = ['杀伤力', '出现频率', '检测难度']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

ax = axes[1]
ax.remove()
ax = fig.add_subplot(1, 2, 2, polar=True)

colors_radar = ['#FF0080', '#7C3AED', '#00D4FF', '#FFB800', '#FF4D6D']
for idx, (name, p) in enumerate(pitfalls.items()):
    values = [p['kill'], p['freq'], p['detect']]
    values += values[:1]
    ax.plot(angles, values, linewidth=2, color=colors_radar[idx], label=name)
    ax.fill(angles, values, alpha=0.08, color=colors_radar[idx])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
ax.set_ylim(0, 10)
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9, color='gray')
ax.grid(True, alpha=0.4)
ax.set_title('5 大误区雷达图', fontsize=13, fontweight='bold', pad=20)
ax.legend(loc='center left', bbox_to_anchor=(1.15, 0.5), fontsize=10)

plt.tight_layout()
plt.show()
