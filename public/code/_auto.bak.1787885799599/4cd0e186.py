# @quantlab/output: 4cd0e186
# Feast 在量化场景下的概念映射
"""
量化 Feature Store (Feast):

Entity:
  - stock: 股票实体
  - futures_contract: 期货合约实体

FeatureView:
  - stock_price_features:
      数据源: daily_market_data
      特征: [daily_return, volume, vwap, volatility_20d]
      实体: stock

  - stock_fundamental_features:
      数据源: quarterly_financials
      特征: [pe_ratio, pb_ratio, roe, debt_to_equity]
      实体: stock
      注意：需要 point-in-time join 避免 look-ahead bias

FeatureService:
  - momentum_strategy_features: [daily_return, volatility_20d,
                                  volume, pe_ratio]
  - mean_reversion_features: [daily_return, z_score_20d, rsi_14d]

Online Store (Redis):
  - 存储最新的特征值，供实时策略查询
  - key: stock:{symbol}:feature:{feature_name}
  - value: 最新的特征值

Offline Store (Parquet on S3/MinIO):
  - 存储历史特征值，供回测使用
  - 分区: feature_name / date
"""
