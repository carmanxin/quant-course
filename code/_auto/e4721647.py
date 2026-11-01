# @quantlab/output: e4721647
class AutoRepair:
    """
    自动修复常见数据质量问题。

    修复策略分层：
    1. 可直接修复的问题（如数据格式）
    2. 可推断修复的问题（如用前后值插补）
    3. 需标记后人工审核的问题
    """

    @staticmethod
    def repair_duplicate_timestamps(data: pd.DataFrame,
                                     timestamp_col: str = 'timestamp',
                                     strategy: str = 'keep_last') -> pd.DataFrame:
        """
        修复重复时间戳。

        策略:
        - 'keep_last': 保留最后一次出现的记录
        - 'keep_first': 保留第一次
        - 'average_price': 对成交价取成交量加权平均
        """
        if strategy == 'keep_last':
            return data.drop_duplicates(subset=[timestamp_col], keep='last')
        elif strategy == 'keep_first':
            return data.drop_duplicates(subset=[timestamp_col], keep='first')
        elif strategy == 'average_price':
            # 成交量加权平均
            grouped = data.groupby(timestamp_col)
            repaired = grouped.agg({
                'price': lambda x: np.average(x, weights=data.loc[x.index, 'size']),
                'size': 'sum'
            }).reset_index()
            return repaired

    @staticmethod
    def interpolate_small_gaps(data: pd.DataFrame,
                                time_col: str = 'timestamp',
                                value_col: str = 'price',
                                max_gap_seconds: int = 5) -> pd.DataFrame:
        """
        对短时间间断进行线性插值修复。

        只修复 max_gap_seconds 内的短间断，
        长间断保留为空（标记为质量问题）。
        """
        data = data.sort_values(time_col).reset_index(drop=True)
        data['time_diff'] = data[time_col].diff().dt.total_seconds()

        # 识别短间断
        short_gaps = (data['time_diff'] > 0) & \
                     (data['time_diff'] <= max_gap_seconds)

        if short_gaps.any():
            data[value_col] = data[value_col].interpolate(
                method='linear',
                limit=1  # 每个间断只补一个点
            )
            data['interpolated'] = short_gaps

        return data

    @staticmethod
    def flag_for_review(data: pd.DataFrame,
                         anomaly_mask: np.ndarray,
                         issue_type: str) -> pd.DataFrame:
        """
        标记异常记录，添加质量标记字段。

        通过添加 data_quality_flag 和 review_required 字段，
        保留数据供后续分析的同时标记其可信度。
        """
        data = data.copy()
        data['data_quality_flag'] = data.get('data_quality_flag', 'CLEAN')
        data.loc[anomaly_mask, 'data_quality_flag'] = issue_type
        data['review_required'] = data['data_quality_flag'] != 'CLEAN'

        return data
