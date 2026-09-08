# @quantlab/output: 50ce70cc
class TickDataIndex:
    """
    Tick 数据的多层索引设计。

    索引层级：
    1. 分区层：按日期和 symbol 进行文件系统分区（避免扫描无关文件）
    2. 文件内元数据：Parquet 的 footer 中存储 min/max 统计
    3. 内存缓存：热点数据的内存映射
    """

    @staticmethod
    def build_symbol_date_catalog(base_path: str) -> pd.DataFrame:
        """
        构建 symbol-date 目录索引，加速查询路由。
        """
        base = Path(base_path)
        entries = []

        for symbol_dir in base.iterdir():
            if symbol_dir.is_dir():
                symbol = symbol_dir.name
                for date_dir in symbol_dir.iterdir():
                    if date_dir.is_dir():
                        date_str = date_dir.name
                        parquet_files = list(date_dir.glob('*.parquet'))
                        total_size = sum(f.stat().st_size
                                         for f in parquet_files)

                        entries.append({
                            'symbol': symbol,
                            'date': date_str,
                            'file_count': len(parquet_files),
                            'total_size_bytes': total_size,
                            'path': str(date_dir)
                        })

        catalog = pd.DataFrame(entries)
        catalog['date'] = pd.to_datetime(catalog['date'])
        catalog = catalog.sort_values(['symbol', 'date'])

        return catalog

    @staticmethod
    def query_plan(catalog: pd.DataFrame,
                   symbols: list,
                   start_date: str,
                   end_date: str) -> list:
        """
        给定查询条件，返回需要读取的文件列表（避免全表扫描）。
        """
        mask = (
            catalog['symbol'].isin(symbols) &
            (catalog['date'] >= start_date) &
            (catalog['date'] <= end_date)
        )
        relevant = catalog[mask]

        files_to_read = []
        for _, row in relevant.iterrows():
            for f in Path(row['path']).glob('*.parquet'):
                files_to_read.append(str(f))

        return files_to_read
