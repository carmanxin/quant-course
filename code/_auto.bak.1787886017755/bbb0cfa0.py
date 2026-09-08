# @quantlab/output: bbb0cfa0
def svensson(tau, beta0, beta1, beta2, beta3, lam1, lam2):
    """Svensson 扩展模型"""
    x1 = tau / lam1
    x2 = tau / lam2
    f1 = (1 - np.exp(-x1)) / x1
    f2 = (1 - np.exp(-x2)) / x2
    return (
        beta0
        + beta1 * f1
        + beta2 * (f1 - np.exp(-x1))
        + beta3 * (f2 - np.exp(-x2))
    )
