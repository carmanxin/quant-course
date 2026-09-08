# @quantlab/output: 7fff9b16
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

# 按 dtype 估算单条记录的字节数，进而推算全市场存储规模
DTYPE_BYTES = {
    'datetime64[ns]': 8, 'float64': 8, 'int64': 8, 'bool': 1,
    'str': 12,  # 字典编码/LowCardinality 后的近似值
}


def schema_report(name, schema):
    row_bytes = sum(DTYPE_BYTES[t] for t in schema.values())
    print(f"=== {name}（{len(schema)} 字段，{row_bytes} bytes/行）===")
    for field, dtype in schema.items():
        print(f"  {field:<18}{dtype:<18}{DTYPE_BYTES[dtype]:>3} B")
    print()
    return row_bytes


trade_row = schema_report('TICK_TRADE_SCHEMA', TICK_TRADE_SCHEMA)
quote_row = schema_report('TICK_QUOTE_SCHEMA', TICK_QUOTE_SCHEMA)

# 存储量估算：A 股全市场约 5000 只标的
N_SYMBOLS, N_DAYS = 5000, 252
TRADES_PER_SYMBOL_DAY = 20_000     # 活跃标的日均成交笔数量级
QUOTES_PER_SYMBOL_DAY = 200_000    # 报价更新远多于成交
COMPRESS_RATIO = 15                # 列式存储 + delta/字典编码的典型压缩比

raw_trade = trade_row * TRADES_PER_SYMBOL_DAY * N_SYMBOLS * N_DAYS
raw_quote = quote_row * QUOTES_PER_SYMBOL_DAY * N_SYMBOLS * N_DAYS
raw_total = raw_trade + raw_quote

print(f"=== 全市场一年 Tick 存储估算（{N_SYMBOLS} 标的 × {N_DAYS} 交易日）===")
print(f"  成交流水 原始:      {raw_trade / 1e12:>7.2f} TB")
print(f"  报价快照 原始:      {raw_quote / 1e12:>7.2f} TB")
print(f"  合计     原始:      {raw_total / 1e12:>7.2f} TB")
print(f"  列式压缩后（{COMPRESS_RATIO}x）: {raw_total / COMPRESS_RATIO / 1e12:>7.2f} TB")
print(f"\n结论：报价流量约为成交流量的 {raw_quote / raw_trade:.0f} 倍，"
      f"quote 表才是存储与查询成本的主要来源。")
