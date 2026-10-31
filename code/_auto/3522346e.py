# @quantlab/output: 3522346e
def broadcasting_examples():
    """
    NumPy 广播机制是量化计算加速的关键
    """
    # 示例：计算所有股票对的价格比率
    prices = np.array([10, 20, 30, 40, 50])  # (5,)
    ratios = prices[:, np.newaxis] / prices[np.newaxis, :]  # (5, 5)

    # 示例：按行/列标准化
    returns = np.random.randn(100, 50)  # 100天, 50只股票
    row_mean = returns.mean(axis=1, keepdims=True)  # (100, 1)
    row_std = returns.std(axis=1, keepdims=True)    # (100, 1)
    normalized = (returns - row_mean) / row_std

    return normalized
