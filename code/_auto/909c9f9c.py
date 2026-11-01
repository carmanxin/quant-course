# @quantlab/output: 909c9f9c
from scipy.stats import spearmanr
ic = df.groupby('date').apply(lambda x: spearmanr(x['factor'], x['fwd_return'])[0])
print(f"IC均值: {ic.mean():.4f}")
