# @quantlab/output: fefaad0e
def threshold_selection(returns: np.ndarray,
                         method: str = 'mean_excess') -> float:
    """
    选择POT方法的阈值 u。

    方法 'mean_excess': 平均超出函数 (Mean Excess Function)
       e(u) = E[X - u | X > u]，在线性区域选择阈值

    方法 'quantile': 取指定的分位数

    参数:
        returns: 收益率（以损失为正，即对多头用 -returns）
        method: 阈值选择方法
    返回:
        建议的阈值 u
    """
    if method == 'quantile':
        # 取90%或95%分位数
        return np.percentile(returns, 90)

    elif method == 'mean_excess':
        sorted_losses = np.sort(returns)
        n = len(sorted_losses)

        # 计算各候选阈值的平均超出量
        thresholds = np.linspace(np.percentile(returns, 80),
                                 np.percentile(returns, 98),
                                 50)
        mean_excess = []

        for u in thresholds:
            exceedances = sorted_losses[sorted_losses > u] - u
            if len(exceedances) > 10:
                mean_excess.append(np.mean(exceedances))
            else:
                mean_excess.append(np.nan)

        # 寻找线性区域的起始点
        # 简化：取使平均超出量开始线性增长的阈值
        diffs = np.diff(mean_excess)
        for i in range(len(diffs) - 1):
            if abs(diffs[i+1] - diffs[i]) < 0.01 * np.std(returns):
                return thresholds[i]

        return np.percentile(returns, 90)  # 默认
