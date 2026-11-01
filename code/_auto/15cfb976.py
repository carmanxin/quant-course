# @quantlab/output: 15cfb976
def tick_data_compression_benchmark(sample_data: pd.DataFrame) -> dict:
    """
    比较不同压缩算法对 Tick 数据的压缩效果。

    Tick 数据的特殊性：
    - timestamp 列具有高局部性（delta 编码极有效）
    - price 列增量通常很小（适合 delta + 熵编码）
    - size 列分布不均
    - symbol 列低基数（字典编码极有效）
    """
    import time
    import io

    results = {}
    compressions = ['snappy', 'gzip', 'zstd', 'lz4', 'brotli']

    for comp in compressions:
        buf = io.BytesIO()

        start = time.time()
        table = pa.Table.from_pandas(sample_data)

        pq.write_table(table, buf,
                        compression=comp,
                        use_dictionary=True)

        compressed_size = buf.tell()
        original_size = sample_data.memory_usage(deep=True).sum()
        ratio = original_size / compressed_size
        elapsed = time.time() - start

        results[comp] = {
            'compressed_bytes': compressed_size,
            'original_bytes': original_size,
            'compression_ratio': ratio,
            'write_time_seconds': elapsed
        }

    return results
