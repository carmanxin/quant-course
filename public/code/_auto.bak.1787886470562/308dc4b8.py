# @quantlab/output: 308dc4b8
# Tick 数据的标准化 Schema
TICK_TRADE_SCHEMA = {
    'timestamp': 'datetime64[ns]',    # 成交时间戳（纳秒精度）
    'symbol': 'str',                  # 股票代码
    'exchange': 'str',                # 交易所代码
    'price': 'float64',               # 成交价
    'size': 'int64',                  # 成交量
    'trade_id': 'int64',              # 成交编号
    'trade_condition': 'str',         # 成交条件（如 @, F, I 等）
    'bid_price': 'float64',           # 成交时的最优买价
    'ask_price': 'float64',           # 成交时的最优卖价
}

TICK_QUOTE_SCHEMA = {
    'timestamp': 'datetime64[ns]',    # 报价时间戳
    'symbol': 'str',
    'exchange': 'str',
    'bid_price': 'float64',           # 最优买价
    'bid_size': 'int64',              # 最优买价挂单量
    'ask_price': 'float64',           # 最优卖价
    'ask_size': 'int64',              # 最优卖价挂单量
    'bid_exchange': 'str',            # 最优买价来源交易所
    'ask_exchange': 'str',
    'quote_condition': 'str',
    'nbbo_indicator': 'bool',         # 是否为 NBBO
}
