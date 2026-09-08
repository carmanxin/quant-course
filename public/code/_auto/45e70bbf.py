# @quantlab/output: 45e70bbf
def build_point_in_time_universe(data_provider, date):
    """
    使用点对点数据构建当日的可交易股票池
    包括当日实际存在的所有股票（不仅仅是现在还在交易的）
    """
    # 使用点对点（Point-in-Time）数据库
    # 每个日期都有该日期对应的股票列表
    universe = data_provider.get_tradeable_stocks(date)

    # 过滤条件（基于当日已知信息）
    universe = universe[(universe['market_cap'] > 1e9) &  # 市值>10亿
                         (universe['avg_daily_volume'] > 1e6) &  # 日均成交额>100万
                         (not universe['is_suspended']) &  # 不处于停牌状态
                         (not universe['is_st'])  # 非ST股票
                        ]

    return universe
