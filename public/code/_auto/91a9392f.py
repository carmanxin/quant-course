# @quantlab/output: 91a9392f
def tick_query_optimizer(query_type: str,
                          params: dict) -> str:
    """
    根据查询类型和参数生成优化后的查询策略。

    Tick数据的典型查询模式：
    1. 时间范围查询（某一天某只股票的所有tick）
    2. 快照查询（某一时刻全市场的状态）
    3. 聚合查询（计算分钟/小时K线）
    4. 模式查询（查找特定模式，如大单、快速价格变动）
    """
    strategies = {
        'time_range_single_symbol': {
            'partition_pruning': True,
            'min_max_filter': True,
            'parallel_reads': 1,       # 单品种线形读取足够
            'use_precomputed_bars': False
        },
        'market_snapshot': {
            'partition_pruning': True,
            'min_max_filter': True,
            'parallel_reads': 8,       # 多品种并行读取
            'use_precomputed_bars': False
        },
        'aggregation_all_symbols': {
            'partition_pruning': True,
            'min_max_filter': False,   # 聚合不需要精确过滤
            'parallel_reads': 16,      # 高度并行
            'use_precomputed_bars': True # 用物化视图加速
        },
        'pattern_detection': {
            'partition_pruning': True,
            'min_max_filter': True,
            'parallel_reads': 4,
            'use_precomputed_bars': False,
            'push_predicate_to_read': True  # 谓词下推
        }
    }

    return strategies.get(query_type, strategies['time_range_single_symbol'])
