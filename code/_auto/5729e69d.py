# @quantlab/output: 5729e69d
# ClickHouse MergeTree 表定义（适用于 Tick 数据）
DDL_TICK_TRADES = """
CREATE TABLE IF NOT EXISTS tick_trades (
    timestamp       DateTime64(9, 'UTC'),
    symbol          LowCardinality(String),
    exchange        LowCardinality(String),
    price           Float64,
    size            UInt64,
    trade_id        UInt64,
    trade_condition LowCardinality(String),
    bid_price       Float64,
    ask_price       Float64,
    insert_time     DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)  -- 按日分区
ORDER BY (symbol, timestamp)        -- 排序键：先 symbol 后时间
TTL timestamp + INTERVAL 30 DAY     -- 30天自动过期（按需调整）
SETTINGS index_granularity = 8192;  -- 稀疏索引粒度
"""

# 物化视图：预聚合 1 分钟 K 线（写入 tick_trades 时增量维护）
DDL_MINUTE_BARS = """
CREATE MATERIALIZED VIEW tick_minute_bars
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (symbol, timestamp)
AS SELECT
    symbol,
    toStartOfMinute(timestamp) AS timestamp,
    argMin(price, timestamp) AS open,
    max(price) AS high,
    min(price) AS low,
    argMax(price, timestamp) AS close,
    sum(size) AS volume,
    count() AS trade_count
FROM tick_trades
GROUP BY symbol, timestamp;
"""

MIGRATIONS = [('tick_trades', DDL_TICK_TRADES), ('tick_minute_bars', DDL_MINUTE_BARS)]


def apply_migrations(client=None):
    """真实环境传入 clickhouse_driver.Client；这里没有连接就只做 dry-run。"""
    for name, ddl in MIGRATIONS:
        stmt = ddl.strip()
        if client is None:
            print(f"[dry-run] would execute DDL for {name} ({len(stmt)} chars, "
                  f"{len(stmt.splitlines())} lines)")
        else:
            client.execute(stmt)
            print(f"[applied] {name}")


apply_migrations()          # 未连接 ClickHouse → dry-run

print("\n=== 设计要点 ===")
DESIGN_NOTES = [
    ('ENGINE',            'MergeTree',                 '后台归并有序数据块，写入吞吐高'),
    ('PARTITION BY',      'toYYYYMMDD(timestamp)',     '按日分区 → 时间范围查询直接裁掉无关分区'),
    ('ORDER BY',          '(symbol, timestamp)',       '先 symbol 后时间：单票时间序列扫描连续'),
    ('LowCardinality',    'symbol / exchange',         '字典编码，重复字符串只存一次'),
    ('TTL',               'timestamp + 30 DAY',        '热数据留 30 天，过期自动落冷/删除'),
    ('index_granularity', '8192',                      '稀疏索引：每 8192 行一个标记'),
]
for k, v, why in DESIGN_NOTES:
    print(f"  {k:<18}{v:<26}{why}")

# 稀疏索引 + 分区裁剪的效果：查 1 只票 1 天的 tick
TOTAL_ROWS = 5000 * 252 * 20_000        # 全市场一年成交流水行数
ROWS_PER_SYMBOL_DAY = 20_000
GRANULARITY = 8192
partition_rows = 5000 * ROWS_PER_SYMBOL_DAY          # 单日分区行数
granules_scanned = max(1, ROWS_PER_SYMBOL_DAY // GRANULARITY + 1)

print("\n=== 查询 “某只票某一天的全部 tick” 的扫描量 ===")
print(f"  全表行数:            {TOTAL_ROWS:>15,}")
print(f"  分区裁剪后:          {partition_rows:>15,}  ({partition_rows / TOTAL_ROWS:.4%})")
print(f"  稀疏索引命中 granule: {granules_scanned:>15,} 个 "
      f"→ 实际读取约 {granules_scanned * GRANULARITY:,} 行")
print(f"  相对全表扫描节省:    {1 - granules_scanned * GRANULARITY / TOTAL_ROWS:.6%}")

print("\n=== 排序键顺序的影响 ===")
print("  ORDER BY (symbol, timestamp) → 单票回放快；跨票同一时刻切片慢")
print("  ORDER BY (timestamp, symbol) → 全市场快照快；单票回放要跳着读")
print("  两类查询都重要时，用第二张表或 PROJECTION 各存一份排序")
