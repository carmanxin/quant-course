# @quantlab/output: 34631723
from statsmodels.tsa.stattools import coint
score, pvalue, _ = coint(df['X'], df['Y'])
print(f"协整检验p值: {pvalue:.4f}")
