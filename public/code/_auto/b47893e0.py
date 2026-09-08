# @quantlab/output: b47893e0
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error

def build_stock_selection_pipeline(factor_data, returns, n_splits=5):
    """
    完整的监督学习选股流水线

    factor_data: DataFrame, index=日期, columns=股票x因子 (MultiIndex)
    returns: DataFrame, index=日期, columns=股票, values=未来N日收益率
    """
    # 1. 构建特征矩阵和标签
    X = factor_data.copy()
    y = returns.stack()  # 将宽表转为长表

    # 2. 处理极端值和缺失值
    # 截面中性化（跨股票标准化）
    X = X.groupby(level='date').transform(
        lambda x: (x - x.median()) / (x.quantile(0.75) - x.quantile(0.25))
    )
    X = X.clip(-3, 3)  # Winsorize
    X = X.fillna(0)

    # 3. 时序交叉验证（避免前视偏差）
    tscv = TimeSeriesSplit(n_splits=n_splits)
    dates = sorted(set(X.index.get_level_values('date')))

    fold_results = []
    feature_importances = []
    predictions = []

    for fold, (train_dates_idx, test_dates_idx) in enumerate(tscv.split(dates)):
        train_dates = [dates[i] for i in train_dates_idx]
        test_dates = [dates[i] for i in test_dates_idx]

        # 分割训练和测试样本
        X_train = X.loc[train_dates]
        X_test = X.loc[test_dates]
        y_train = y.loc[train_dates]
        y_test = y.loc[test_dates]

        # 4. 训练模型
        model = XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.7,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # 5. 预测与评估
        y_pred = model.predict(X_test)

        # 计算Rank IC
        from scipy.stats import spearmanr
        ic = spearmanr(y_test, y_pred)[0]

        # 按日期分别计算IC
        daily_ic = []
        for date in test_dates:
            mask = X_test.index.get_level_values('date') == date
            if mask.sum() > 10:  # 至少10只股票
                ic_d = spearmanr(y_test.loc[date], y_pred[mask])[0]
                daily_ic.append(ic_d)

        fold_results.append({
            'fold': fold,
            'IC': ic,
            'IC_mean': np.mean(daily_ic),
            'IC_std': np.std(daily_ic),
            'ICIR': np.mean(daily_ic) / np.std(daily_ic) if np.std(daily_ic) > 0 else 0,
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'train_period': f"{train_dates[0]} ~ {train_dates[-1]}",
            'test_period': f"{test_dates[0]} ~ {test_dates[-1]}"
        })

        # 6. 特征重要性
        importance = pd.Series(
            model.feature_importances_,
            index=X.columns
        ).sort_values(ascending=False)
        feature_importances.append(importance)

        predictions.append(pd.DataFrame({
            'y_true': y_test.values,
            'y_pred': y_pred,
        }, index=y_test.index))

    # 汇总结果
    results_df = pd.DataFrame(fold_results)
    avg_importance = pd.concat(feature_importances, axis=1).mean(axis=1).sort_values(ascending=False)

    print("=" * 60)
    print("监督学习选股回测结果")
    print("=" * 60)
    print(f"平均IC:     {results_df['IC_mean'].mean():.4f}")
    print(f"IC标准差:   {results_df['IC_std'].mean():.4f}")
    print(f"ICIR:        {results_df['ICIR'].mean():.4f}")
    print(f"平均RMSE:   {results_df['RMSE'].mean():.4f}")
    print(f"\nTop 10 重要因子:")
    for i, (factor, imp) in enumerate(avg_importance.head(10).items()):
        print(f"  {i+1}. {factor}: {imp:.4f}")

    return {
        'model': model,
        'fold_results': results_df,
        'importance': avg_importance,
        'predictions': pd.concat(predictions)
    }

# ===== 示例数据生成 =====
np.random.seed(42)
n_dates = 500
n_stocks = 300

# 模拟因子数据（10个因子）
factor_names = ['momentum_1m', 'momentum_3m', 'volatility', 'turnover',
                'size', 'value', 'quality', 'growth', 'leverage', 'reversal']
dates = pd.date_range('2020-01-01', periods=n_dates, freq='B')

# 构建 MultiIndex DataFrame
arrays = []
for date in dates:
    for stock in range(n_stocks):
        arrays.append((date, f'STOCK_{stock:04d}'))
index = pd.MultiIndex.from_tuples(arrays, names=['date', 'stock'])

factors = pd.DataFrame(
    np.random.randn(len(index), len(factor_names)),
    index=index,
    columns=factor_names
)

# 模拟未来收益率（加入与某些因子的真实关系）
true_alpha = (
    0.5 * factors['momentum_1m'] +
    0.3 * factors['quality'] -
    0.4 * factors['volatility'] +
    0.2 * factors['value'] +
    np.random.randn(len(factors)) * 0.5  # 噪声
)
returns = pd.Series(true_alpha, index=index)

print("注意：以上为示例数据。实际应用中factor_data和returns需使用真实数据。")
