# @quantlab/output: be5f3491
df['SUE'] = (df['eps_actual'] - df['eps_estimate']) / df['eps_estimate'].std()
df['alpha'] = np.where(df['SUE'] > 1, 1, -1)
