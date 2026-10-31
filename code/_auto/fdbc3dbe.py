# @quantlab/output: fdbc3dbe
# Feast 在量化场景下的概念映射（用纯 Python 表达，便于校验与生成 Feast 定义文件）
import pandas as pd

ENTITIES = {
    'stock': 'join_key=symbol，A 股 6 位代码',
    'futures_contract': 'join_key=contract_id，如 IF2403',
}

FEATURE_VIEWS = {
    'stock_price_features': {
        'entity': 'stock',
        'source': 'daily_market_data',
        'ttl_days': 3,
        'features': ['daily_return', 'volume', 'vwap', 'volatility_20d'],
        'note': '日频行情，T+0 收盘后即可用',
    },
    'stock_fundamental_features': {
        'entity': 'stock',
        'source': 'quarterly_financials',
        'ttl_days': 120,
        'features': ['pe_ratio', 'pb_ratio', 'roe', 'debt_to_equity'],
        'note': '季频财报，必须按「公告日」而非「报告期」做 point-in-time join',
    },
}

FEATURE_SERVICES = {
    'momentum_strategy_features': ['daily_return', 'volatility_20d', 'volume', 'pe_ratio'],
    'mean_reversion_features': ['daily_return', 'z_score_20d', 'rsi_14d'],
}

ONLINE_STORE = {'type': 'Redis', 'key_pattern': 'stock:{symbol}:feature:{feature_name}'}
OFFLINE_STORE = {'type': 'Parquet on S3/MinIO', 'partition': 'feature_name / date'}

print("=== Entity ===")
for name, desc in ENTITIES.items():
    print(f"  {name:<20}{desc}")

print("\n=== FeatureView ===")
for name, fv in FEATURE_VIEWS.items():
    print(f"  {name}  (entity={fv['entity']}, source={fv['source']}, ttl={fv['ttl_days']}d)")
    print(f"      features: {', '.join(fv['features'])}")
    print(f"      note: {fv['note']}")

print("\n=== FeatureService（模型消费的特征组合）===")
declared = {f for fv in FEATURE_VIEWS.values() for f in fv['features']}
for svc, feats in FEATURE_SERVICES.items():
    missing = [f for f in feats if f not in declared]
    status = 'OK' if not missing else f"缺少定义: {missing}"
    print(f"  {svc:<32}{len(feats)} 个特征  [{status}]")

print(f"\nOnline  Store: {ONLINE_STORE['type']}，key = {ONLINE_STORE['key_pattern']}")
print(f"Offline Store: {OFFLINE_STORE['type']}，分区 = {OFFLINE_STORE['partition']}")

# ===== point-in-time join：Feast get_historical_features 的核心语义 =====
# 财报「报告期」是 2024Q1，但真正可用的时间是「公告日」。
# 用报告期对齐 = 未来函数；用公告日对齐 = 正确。
fundamentals = pd.DataFrame({
    'symbol': ['600519'] * 3,
    'report_period': pd.to_datetime(['2023-12-31', '2024-03-31', '2024-06-30']),
    'announce_date': pd.to_datetime(['2024-03-29', '2024-04-27', '2024-08-09']),
    'roe': [0.310, 0.082, 0.171],
})
signal_dates = pd.DataFrame({
    'symbol': ['600519'] * 4,
    'event_timestamp': pd.to_datetime(['2024-04-01', '2024-04-26', '2024-05-06', '2024-08-12']),
})

wrong = pd.merge_asof(signal_dates.sort_values('event_timestamp'),
                      fundamentals.sort_values('report_period'),
                      left_on='event_timestamp', right_on='report_period',
                      by='symbol', direction='backward')
right = pd.merge_asof(signal_dates.sort_values('event_timestamp'),
                      fundamentals.sort_values('announce_date'),
                      left_on='event_timestamp', right_on='announce_date',
                      by='symbol', direction='backward')

cmp = pd.DataFrame({
    '取数日': signal_dates['event_timestamp'].dt.date,
    '按报告期(错)': wrong['roe'].values,
    '按公告日(对)': right['roe'].values,
})
print("\n=== point-in-time join 对照 ===")
print(cmp.to_string(index=False))
n_bad = int((cmp['按报告期(错)'] != cmp['按公告日(对)']).sum())
print(f"\n{n_bad}/{len(cmp)} 个取数日出现未来函数：按报告期对齐会提前拿到尚未公告的 ROE。")
print("Feast 的 get_historical_features 靠 event_timestamp + ttl 自动规避这个坑。")
