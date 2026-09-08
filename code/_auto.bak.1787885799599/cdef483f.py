# @quantlab/output: cdef483f
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def write_tick_to_parquet(tick_data: pd.DataFrame,
                           base_path: str,
                           partition_by: str = 'date') -> list:
    """
    将 Tick 数据写入分区 Parquet 文件。

    推荐分区方案：
    /data/trades/{symbol}/{date}/{symbol}_{date}_{hour}.parquet
    /data/quotes/{symbol}/{date}/{symbol}_{date}_{hour}.parquet

    参数:
        tick_data: Tick 数据 DataFrame（含 symbol, timestamp 列）
        base_path: 存储根目录
        partition_by: 分区方式 'date' 或 'symbol_date'
    返回:
        写入的文件路径列表
    """
    written_files = []

    # 添加日期列用于分区
    tick_data['date'] = tick_data['timestamp'].dt.date
    tick_data['hour'] = tick_data['timestamp'].dt.hour

    # 按 (symbol, date) 分组
    for (symbol, date), group in tick_data.groupby(['symbol', 'date']):
        # 文件路径
        date_str = date.strftime('%Y%m%d')
        symbol_dir = Path(base_path) / symbol / date_str
        symbol_dir.mkdir(parents=True, exist_ok=True)

        # 按小时切分文件（控制文件大小）
        for hour, hour_group in group.groupby('hour'):
            filename = f"{symbol}_{date_str}_{hour:02d}.parquet"
            filepath = symbol_dir / filename

            # 写 Parquet，使用 Snappy 压缩
            table = pa.Table.from_pandas(
                hour_group.drop(columns=['date', 'hour'])
            )
            pq.write_table(
                table, str(filepath),
                compression='snappy',
                row_group_size=100000,  # 每个行组10万行
                use_dictionary=True,     # 字典编码（适合 symbol 等低基数列）
                write_statistics=True    # 写入列统计（min/max/null_count）
            )

            written_files.append(str(filepath))

    return written_files
