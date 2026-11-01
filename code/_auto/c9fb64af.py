# @quantlab/output: c9fb64af
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def market_regime_clustering(returns_df, n_regimes=4, lookback=20):
    """
    使用K-Means对市场状态进行聚类，识别不同Regime

    returns_df: DataFrame, index=日期, columns=资产收益率
    n_regimes: 聚类数
    lookback: 回看窗口（用于计算滚动统计量）
    """
    # 构建Regime特征
    features = pd.DataFrame(index=returns_df.index)

    # 1. 市场平均收益率和波动率
    features['mean_ret'] = returns_df.mean(axis=1).rolling(lookback).mean()
    features['volatility'] = returns_df.std(axis=1).rolling(lookback).mean()

    # 2. 相关性水平（平均成对相关性）
    rolling_corr = returns_df.rolling(lookback).corr()
    # 简化处理：每个时间点的平均相关性
    avg_corr = []
    for i in range(lookback, len(returns_df)):
        corr_mat = returns_df.iloc[i-lookback:i].corr()
        upper_tri = corr_mat.values[np.triu_indices_from(corr_mat.values, k=1)]
        avg_corr.append(np.mean(np.abs(upper_tri)))
    features.loc[features.index[lookback:], 'avg_corr'] = avg_corr

    # 3. 趋势强度（正收益率比例）
    features['trend_strength'] = (returns_df > 0).mean(axis=1).rolling(lookback).mean()

    # 4. 尾部风险（极值收益率频率）
    features['tail_risk'] = (returns_df < -0.02).mean(axis=1).rolling(lookback).mean()

    # 去除NaN
    features = features.dropna()

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # K-Means聚类
    kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # 分析每个Regime的特征
    results = pd.DataFrame(X_scaled, index=features.index,
                          columns=features.columns)
    results['regime'] = labels

    print("市场Regime特征（均值）:")
    print("=" * 60)
    for r in range(n_regimes):
        regime_data = results[results['regime'] == r]
        n_days = len(regime_data)
        print(f"\nRegime {r} ({n_days} 个交易日, {n_days/len(results)*100:.1f}%):")
        for col in features.columns:
            original_val = regime_data[col].mean() * scaler.scale_[features.columns.get_loc(col)] + scaler.mean_[features.columns.get_loc(col)]
            print(f"  {col}: {original_val:.4f}")

    return results, kmeans

# 示例
np.random.seed(42)
dates = pd.date_range('2020-01-01', periods=500, freq='B')
sample_ret = pd.DataFrame(
    np.random.randn(500, 10) * 0.01,
    index=dates,
    columns=[f'Asset_{i}' for i in range(10)]
)

regime_results, model = market_regime_clustering(sample_ret, n_regimes=3)
