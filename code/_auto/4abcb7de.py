# @quantlab/output: 4abcb7de
class AnomalyDetector:
    """
    多级异常值检测器。

    检测策略：
    Level 1: 静态规则（如价格 > 0, Ask > Bid）
    Level 2: 统计规则（如 Z-score, MAD-based）
    Level 3: 时序规则（如前后价格变动过大）
    """

    @staticmethod
    def level1_static_rules(row: pd.Series) -> List[str]:
        """一级：静态合理性规则"""
        violations = []

        if row.get('price', 0) <= 0:
            violations.append('PRICE_NEGATIVE_OR_ZERO')
        if row.get('size', 0) <= 0:
            violations.append('SIZE_NEGATIVE_OR_ZERO')
        if row.get('ask_price', 0) < row.get('bid_price', 0):
            violations.append('ASK_LESS_THAN_BID')
        if row.get('high', 0) < row.get('low', 0):
            violations.append('HIGH_LESS_THAN_LOW')
        if row.get('close', 0) > row.get('high', 0) or \
           row.get('close', 0) < row.get('low', 0):
            violations.append('CLOSE_OUTSIDE_HL_RANGE')

        return violations

    @staticmethod
    def level2_statistical_rules(data: pd.Series,
                                  method: str = 'iqr',
                                  multiplier: float = 5.0) -> np.ndarray:
        """
        二级：基于统计分布的异常检测。

        参数:
            data: 数值序列
            method: 'iqr' (四分位距) 或 'mad' (中位数绝对偏差)
            multiplier: 判定阈值乘数
        返回:
            布尔数组，True 表示异常
        """
        if method == 'iqr':
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - multiplier * iqr
            upper = q3 + multiplier * iqr
            return (data < lower) | (data > upper)

        elif method == 'mad':
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z = 0.6745 * (data - median) / (mad + 1e-10)
            return np.abs(modified_z) > multiplier

    @staticmethod
    def level3_price_jump(data: pd.DataFrame,
                           max_bps_change: float = 500) -> np.ndarray:
        """
        三级：价格跳变检测。

        检测两笔连续交易间价格的异常跳变（bps）。

        参数:
            data: 含 price 列的时序数据
            max_bps_change: 最大允许的价格变动（基点）
        返回:
            异常标志
        """
        price_change_bps = data['price'].pct_change().abs() * 10000
        return price_change_bps > max_bps_change
