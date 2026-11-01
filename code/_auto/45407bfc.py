# @quantlab/output: 45407bfc
import pandas as pd
df['MA_short'] = df['Close'].rolling(20).mean()
df['MA_long'] = df['Close'].rolling(50).mean()
df['Signal'] = (df['MA_short'] > df['MA_long']).astype(int)
