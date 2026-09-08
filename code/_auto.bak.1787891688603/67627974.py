# @quantlab/output: 67627974
import numpy as np
returns = np.random.randn(1_000_000)
sharpe_np = returns.mean() / returns.std()  # 向量化
