# @quantlab/output: 3a472c94
from scipy import stats


def test_stationarity(series: np.ndarray) -> dict:
    """手动实现简化的 DF 检验"""
    n = len(series)
    delta_y = np.diff(series)
    y_lag = series[:-1]

    # 回归: delta_y_t = gamma * y_{t-1} + e_t
    # 如果 gamma = 0，则存在单位根（非平稳）
    slope, intercept, r_value, p_value, std_err = stats.linregress(y_lag, delta_y)

    # DF 检验的临界值（比标准 t 分布更负）
    # 简化处理：使用 t 统计量
    se = std_err
    t_stat = slope / se

    # 近似的 DF 分布临界值（n=100 时约为 -2.89 at 5%）
    # 这里用绝对值粗略判断
    return {
        'test_statistic': t_stat,
        'p_value': p_value,
        'is_stationary': p_value < 0.05,
        'note': 'p值可能不精确，建议使用 statmodels.adfuller'
    }
