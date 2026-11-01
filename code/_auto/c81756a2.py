# @quantlab/output: c81756a2
from sklearn.ensemble import VotingRegressor, StackingRegressor
from lightgbm import LGBMRegressor
from sklearn.linear_model import Ridge

def ensemble_stock_selection(X_train, y_train, X_test):
    """
    使用多模型集成提升选股稳定性
    """
    base_models = [
        ('xgb', XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)),
        ('lgb', LGBMRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=42)),
        ('ridge', Ridge(alpha=1.0))
    ]

    # 方法1：平均集成
    voting_model = VotingRegressor(base_models)
    voting_model.fit(X_train, y_train)
    voting_pred = voting_model.predict(X_test)

    # 方法2：Stacking集成（使用Ridge作为元学习器）
    stacking_model = StackingRegressor(
        estimators=base_models[:2],  # XGBoost + LightGBM
        final_estimator=Ridge(alpha=1.0),
        cv=5
    )
    stacking_model.fit(X_train, y_train)
    stacking_pred = stacking_model.predict(X_test)

    # 比较
    from scipy.stats import spearmanr

    # 单模型预测
    xgb_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)

    lgb_model = LGBMRegressor(n_estimators=100, max_depth=5, random_state=42)
    lgb_model.fit(X_train, y_train)
    lgb_pred = lgb_model.predict(X_test)

    print("多模型集成效果对比:")
    print(f"{'模型':<15} {'Rank IC':>10} {'MSE':>10}")
    print("-" * 40)
    print(f"{'XGBoost':<15} {spearmanr(y_test, xgb_pred)[0]:>10.4f} "
          f"{mean_squared_error(y_test, xgb_pred):>10.4f}")
    print(f"{'LightGBM':<15} {spearmanr(y_test, lgb_pred)[0]:>10.4f} "
          f"{mean_squared_error(y_test, lgb_pred):>10.4f}")
    print(f"{'Voting':<15} {spearmanr(y_test, voting_pred)[0]:>10.4f} "
          f"{mean_squared_error(y_test, voting_pred):>10.4f}")
    print(f"{'Stacking':<15} {spearmanr(y_test, stacking_pred)[0]:>10.4f} "
          f"{mean_squared_error(y_test, stacking_pred):>10.4f}")

    return voting_model, stacking_model
