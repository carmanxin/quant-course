# @quantlab/output: 8c1412d0
# 量化场景下的引擎选择指南
def recommend_processing_engine(data_volume_gb: float,
                                 latency_requirement_ms: float,
                                 python_ecosystem_required: bool,
                                 existing_infrastructure: str) -> str:
    """
    根据需求推荐最适合的计算引擎。

    参数:
        data_volume_gb: 数据量（GB）
        latency_requirement_ms: 延迟要求（毫秒）
        python_ecosystem_required: 是否必须 Python 生态
        existing_infrastructure: 现有基础设施
    """
    if latency_requirement_ms < 1000:
        return 'Apache Flink'  # 唯一支持亚秒级延迟的
    elif data_volume_gb > 100:
        if existing_infrastructure == 'Hadoop/YARN':
            return 'Apache Spark'
        else:
            return 'Apache Spark (standalone)'
    elif python_ecosystem_required:
        return 'Dask'  # 与 Pandas API 完全兼容
    else:
        return 'Apache Spark'  # 默认推荐
