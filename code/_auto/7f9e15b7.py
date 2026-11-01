# @quantlab/output: 7f9e15b7
ic_weights = ic_mean / ic_std  # ICIR
composite = (factor_df * ic_weights).sum(axis=1)
