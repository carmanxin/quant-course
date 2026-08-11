# 1.7-progress-tracker.py
# 个人量化学习进度跟踪器(2025-2026 版)
# 包含 12 个月时间轴可视化与通过概率估算

import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ============== 个人学习信息(请按实际情况修改) ==============
START_DATE = dt.date(2026, 1, 1)          # 学习开始日期
TARGET_WEEKS = 48                          # 目标完成周期(48 周 = 12 个月)
HOURS_PER_WEEK = 25                        # 每周计划学习时长
TOTAL_CHAPTERS = 20                        # 计划完成的章节总数
COMPLETED_CHAPTERS = 4                     # 截至今天已完成的章节
EFFICIENCY = 1.0                           # 效率系数 (0.5-1.5)

# ============== 当前状态计算 ==============
today = dt.date.today()
weeks_passed = max(1, (today - START_DATE).days // 7)
hours_logged = weeks_passed * HOURS_PER_WEEK * EFFICIENCY

chapter_progress = COMPLETED_CHAPTERS / TOTAL_CHAPTERS
weeks_progress = weeks_passed / TARGET_WEEKS
overall_progress = 0.5 * chapter_progress + 0.5 * min(1.0, weeks_progress)

remaining_chapters = TOTAL_CHAPTERS - COMPLETED_CHAPTERS
chapter_velocity = COMPLETED_CHAPTERS / weeks_passed
weeks_to_finish = remaining_chapters / max(chapter_velocity, 0.1)
estimated_finish = today + dt.timedelta(weeks=int(weeks_to_finish))

# 通过概率:基于累计学时(吸收系数 alpha = 0.0005)
PASS_ALPHA = 0.0005
pass_prob = 1 - np.exp(-PASS_ALPHA * hours_logged)

# ============== 控制台报告 ==============
print('=' * 55)
print('          个 人 量 化 学 习 进 度 跟 踪 器           ')
print('=' * 55)
print(f'开始日期        : {START_DATE}')
print(f'今日日期        : {today}')
print(f'已学习周数      : {weeks_passed} 周')
print(f'已累计学时      : {hours_logged:.0f} 小时')
print(f'章节完成度      : {COMPLETED_CHAPTERS}/{TOTAL_CHAPTERS} ({chapter_progress:.0%})')
print(f'时间进度        : {weeks_passed}/{TARGET_WEEKS} 周 ({weeks_progress:.0%})')
print(f'综合进度        : {overall_progress:.0%}')
print(f'章节完成速度    : {chapter_velocity:.2f} 章/周')
print(f'预计完成日期    : {estimated_finish}')
print('-' * 55)
print(f'通过概率(研究员岗): {pass_prob:.1%}')
print('=' * 55)

# ============== 可视化:进度条 + 时间轴 ==============
fig, axes = plt.subplots(1, 2, figsize=(14, 4))

# 子图 1:三段进度条
progress_items = ['章节完成', '时间投入', '综合进度']
progress_vals = [chapter_progress, weeks_progress, overall_progress]
colors = ['#00E5A0', '#00D4FF', '#7C3AED']

ax = axes[0]
y_pos = np.arange(len(progress_items))
bars = ax.barh(y_pos, progress_vals, color=colors,
               edgecolor='white', linewidth=1.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(progress_items, fontsize=11, fontweight='bold')
ax.set_xlim(0, 1)
ax.set_xlabel('完成度', fontsize=11, fontweight='bold')
ax.set_title('学习进度多维评估', fontsize=13, fontweight='bold')

for bar, val in zip(bars, progress_vals):
    ax.text(val + 0.02, bar.get_y() + bar.get_height() / 2,
            f'{val:.0%}', va='center', fontsize=11, fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, axis='x', alpha=0.3)

# 子图 2:12 个月时间轴
ax = axes[1]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
target_year = 2026
month_dates = [dt.date(target_year, m, 1) for m in range(1, 13)]
month_starts = [(d - START_DATE).days // 7 for d in month_dates]

colors_timeline = []
for start_week in month_starts:
    if start_week <= weeks_passed:
        colors_timeline.append('#00E5A0')    # 已完成
    elif start_week <= weeks_passed + 4:
        colors_timeline.append('#FFB800')    # 进行中
    else:
        colors_timeline.append('#94A3B8')    # 未开始

ax.bar(months, [1] * 12, color=colors_timeline,
       edgecolor='white', linewidth=1.5)
ax.set_ylabel('学习状态', fontsize=11, fontweight='bold')
ax.set_title('12 个月时间轴(2026)', fontsize=13, fontweight='bold')
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

legend = [
    Patch(facecolor='#00E5A0', label='已完成'),
    Patch(facecolor='#FFB800', label='当前阶段'),
    Patch(facecolor='#94A3B8', label='待开始')
]
ax.legend(handles=legend, loc='upper right', fontsize=10)

plt.tight_layout()
plt.show()