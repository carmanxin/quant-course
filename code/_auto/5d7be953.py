# @quantlab/output: 5d7be953
high = df['High'].rolling(20).max()
low = df['Low'].rolling(20).min()
df['signal'] = np.where(df['Close'] > high.shift(1), 1, np.where(df['Close'] < low.shift(1), -1, 0))
