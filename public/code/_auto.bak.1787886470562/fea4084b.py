# @quantlab/output: fea4084b
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
