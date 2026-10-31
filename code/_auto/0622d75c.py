# @quantlab/output: 0622d75c
import pandas as pd
import numpy as np

# 假设已有日内成交量分布数据
df = pd.DataFrame({
    'time_bucket': pd.date_range('2024-01-15 09:30', periods=78, freq='5min'),
    'volume': np.random.gamma(shape=2, scale=5000, size=78)
})

profile = df.groupby('time_bucket')['volume'].sum()
total_volume = profile.sum()
total_order_size = 100000  # 总共需要买入10万股
slice_sizes = (profile / total_volume * total_order_size).astype(int)

print(f"日总成交量: {total_volume:,.0f} 股")
print(f"订单总量: {total_order_size:,.0f} 股,拆分为 {len(slice_sizes)} 个 5 分钟时间片")
print(f"\n前 5 个最活跃时段(开盘/收盘附近):")
for ts, size in slice_sizes.nlargest(5).items():
    print(f"  {ts.strftime('%H:%M')}: {size:>6,} 股")
print(f"\n后 5 个最冷清时段(中午):")
for ts, size in slice_sizes.nsmallest(5).items():
    print(f"  {ts.strftime('%H:%M')}: {size:>6,} 股")
print(f"\n各时段切片总和: {slice_sizes.sum():,} 股 (≈ 订单总量)")
