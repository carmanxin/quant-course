import numpy as np
import pandas as pd
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=60, freq='D')
close = 100 + np.cumsum(np.random.randn(60) * 1.5)
df = pd.DataFrame({'Close': close}, index=dates)
df['MA5'] = df['Close'].rolling(5).mean()
df['MA20'] = df['Close'].rolling(20).mean()
print(df.tail(10).round(2))
print(f'\n最新收盘: {df["Close"].iloc[-1]:.2f}')
print(f'MA5: {df["MA5"].iloc[-1]:.2f}')
print(f'MA20: {df["MA20"].iloc[-1]:.2f}')
