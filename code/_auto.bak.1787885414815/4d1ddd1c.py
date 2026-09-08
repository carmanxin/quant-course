# @quantlab/output: 4d1ddd1c
def svi_variance(k, a, b, rho, m, sigma):
    """
    SVI 参数化——总方差关于 log-moneyness 的函数
    k: 对数行权价 = log(K/S)
    a: 整体水平
    b: 微笑角度
    rho: 偏斜
    m: 水平平移
    sigma: 微笑曲率
    """
    return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))
