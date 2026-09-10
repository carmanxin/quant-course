# @quantlab/output: 83320534
spread = df['stock1'] - hedge_ratio * df['stock2']
zscore = (spread - spread.mean()) / spread.std()
df['position'] = -zscore  # 均值回归
