# @quantlab/output: 55625035
df['Close'] = df['Close'].ffill()
df['Return'] = df['Close'].pct_change()
abnormal = df[df['Return'].abs() > 0.2]
print(f"异常天数: {len(abnormal)}")
