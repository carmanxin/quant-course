# @quantlab/output: 707db625
def cross_source_reconciliation(source_a: pd.DataFrame,
                                 source_b: pd.DataFrame,
                                 key_columns: list,
                                 value_columns: list,
                                 tolerance: dict = None) -> dict:
    """
    跨数据源对账：比较两个数据源的一致性。

    参数:
        source_a, source_b: 两个数据源的 DataFrames
        key_columns: 连接键（如 ['symbol', 'date']）
        value_columns: 要比较的数值列
        tolerance: {列名: 容忍度}，如 {'price': 0.01, 'volume': 100}
    返回:
        对账结果，包含差异统计和详细差异记录
    """
    if tolerance is None:
        tolerance = {}

    # 内连接
    merged = source_a.merge(
        source_b,
        on=key_columns,
        how='outer',
        suffixes=('_A', '_B'),
        indicator=True
    )

    # 只在A/B中存在的记录
    only_in_a = merged[merged['_merge'] == 'left_only']
    only_in_b = merged[merged['_merge'] == 'right_only']
    in_both = merged[merged['_merge'] == 'both']

    # 比较值列
    differences = []
    for col in value_columns:
        col_a = f"{col}_A"
        col_b = f"{col}_B"

        if col_a in in_both.columns and col_b in in_both.columns:
            diff = (in_both[col_a] - in_both[col_b]).abs()
            tol = tolerance.get(col, 0)

            mismatch = diff > tol
            n_mismatch = mismatch.sum()

            if n_mismatch > 0:
                max_diff = diff.max()
                mean_diff = diff[mismatch].mean()
                differences.append({
                    'column': col,
                    'n_mismatches': n_mismatch,
                    'mismatch_rate': n_mismatch / len(in_both) * 100,
                    'max_absolute_diff': max_diff,
                    'mean_absolute_diff': mean_diff
                })

    return {
        'total_records_A': len(source_a),
        'total_records_B': len(source_b),
        'matched_records': len(in_both),
        'only_in_A': len(only_in_a),
        'only_in_B': len(only_in_b),
        'match_rate': len(in_both) / max(len(source_a), len(source_b)) * 100,
        'differences': differences,
        'passes_reconciliation': len(differences) == 0 and
                                  len(only_in_a) == 0 and
                                  len(only_in_b) == 0
    }
