# @quantlab/output: b93d976d
# 错误做法
def slow_correlation_matrix(returns: np.ndarray) -> np.ndarray:
    n = returns.shape[1]
    corr = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            corr[i, j] = np.corrcoef(returns[:, i], returns[:, j])[0, 1]
    return corr

# 正确做法
def fast_correlation_matrix(returns: np.ndarray) -> np.ndarray:
    return np.corrcoef(returns.T)
