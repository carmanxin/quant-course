# @quantlab/output: 4f3f443d
import matplotlib.pyplot as plt
# 一键运行:用 demo 数据 df['Close'/'Open'/'High'/'Low'/'Volume'] 画 K 线图
fig, ax = plt.subplots(figsize=(14, 5))
prices = df[['Open', 'High', 'Low', 'Close']].reset_index(drop=True)
for i, row in prices.iterrows():
    color = 'red' if row['Close'] >= row['Open'] else 'green'
    ax.plot([i, i], [row['Low'], row['High']], 'black', linewidth=0.6)
    ax.plot([i, i], [row['Open'], row['Close']], color, linewidth=4)
ax.set_xlim(-1, len(prices))
ax.set_xlabel('交易日序号')
ax.set_ylabel('价格')
ax.set_title(f'示例 K 线图 ({len(prices)} 个交易日)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
print(f"✅ K 线图已绘制 ({len(prices)} 根日K, 红涨绿跌)")
