# @quantlab/output: 684cfb8a
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

class DataCompletenessChecker:
    """
    数据完整性检查器。

    针对 Tick 数据和日频数据的完整性检查。
    """

    def __init__(self, expected_symbols: list, expected_fields: list):
        self.expected_symbols = set(expected_symbols)
        self.expected_fields = expected_fields
        self.issues = []

    def check_missing_symbols(self,
                               data: pd.DataFrame,
                               date: str) -> Dict[str, List[str]]:
        """
        检查指定日期是否有 symbol 缺失。

        返回:
            {'missing': [...], 'extra': [...]}
        """
        present_symbols = set(data['symbol'].unique())
        missing = self.expected_symbols - present_symbols
        extra = present_symbols - self.expected_symbols

        if missing:
            self.issues.append({
                'type': 'missing_symbols',
                'date': date,
                'symbols': list(missing),
                'severity': 'HIGH'
            })

        return {'missing': list(missing), 'extra': list(extra)}

    def check_time_continuity(self,
                               data: pd.DataFrame,
                               symbol: str,
                               market_open: str,
                               market_close: str,
                               max_gap_minutes: int = 30) -> List[dict]:
        """
        检查某标的在交易时段内是否有超过阈值的间断。

        参数:
            data: 特定 symbol 的数据，需包含 timestamp 列
            symbol: 标的代码
            market_open, market_close: 交易时段（如 '09:30', '16:00'）
            max_gap_minutes: 最大允许间断（分钟）
        """
        data = data.sort_values('timestamp')
        gaps = []
        max_gap = pd.Timedelta(minutes=max_gap_minutes)

        # 检查开盘是否有数据
        open_time = pd.Timestamp(f"{data['timestamp'].iloc[0].date()} {market_open}")
        first_record = data['timestamp'].iloc[0]

        if first_record - open_time > max_gap:
            gaps.append({
                'type': 'late_open',
                'symbol': symbol,
                'expected_open': str(open_time),
                'first_record': str(first_record),
                'gap_seconds': (first_record - open_time).total_seconds()
            })

        # 检查期间是否有间断
        time_diffs = data['timestamp'].diff()
        large_gaps = time_diffs[time_diffs > max_gap]

        for idx in large_gaps.index:
            gaps.append({
                'type': 'data_gap',
                'symbol': symbol,
                'gap_start': str(data.loc[idx, 'timestamp']),
                'gap_duration_seconds': large_gaps[idx].total_seconds(),
                'severity': 'HIGH' if large_gaps[idx].total_seconds() > 3600
                            else 'MEDIUM'
            })

        return gaps

    def check_field_completeness(self,
                                  data: pd.DataFrame) -> Dict[str, float]:
        """
        检查各字段的完整率（非空比例）。
        """
        completeness = {}
        total = len(data)

        for field in self.expected_fields:
            if field in data.columns:
                non_null = data[field].notna().sum()
                completeness[field] = non_null / total * 100

                if completeness[field] < 99.0:
                    self.issues.append({
                        'type': 'field_incompleteness',
                        'field': field,
                        'completeness_pct': completeness[field],
                        'severity': 'HIGH' if completeness[field] < 95.0
                                    else 'MEDIUM'
                    })

        return completeness
