# @quantlab/output: 3.2-data-cleaning
import pandas as pd
import numpy as np
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100, freq='D')
close = 100 + np.cumsum(np.random.randn(100) * 2)
close[50] = np.nan
close[80] = close[79] * 1.5
df = pd.DataFrame({'Close': close}, index=dates)
df['Close'] = df['Close'].ffill()
df['Return'] = df['Close'].pct_change()
abnormal = df[df['Return'].abs() > 0.2]
print(f'缺失值（已前向填充）: 1 处')
print(f'异常收益天数: {len(abnormal)}')
if len(abnormal) > 0:
    print('异常日期:')
    print(abnormal.head())
