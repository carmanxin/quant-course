# @quantlab/output: 25c7ffe4
cov = returns.cov()
vols = np.sqrt(np.diag(cov))
weights = 1 / vols
weights /= weights.sum()
