# @quantlab/output: 822898c1
from sklearn.model_selection import TimeSeriesSplit

def purged_kfold_cv(strategy_params_list, returns_data, n_splits=5, purge_days=10):
    """
    带清洗期的时序交叉验证
    清洗期：训练集和测试集之间留出间隔，避免信号相关性泄漏
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)

    results = []
    for train_idx, test_idx in tscv.split(returns_data):
        # 清洗：在训练集末尾和测试集开头之间留出间隔
        train_end = train_idx[-1] - purge_days
        train_idx = train_idx[train_idx <= train_end]

        train_data = returns_data[train_idx]
        test_data = returns_data[test_idx]

        # 在训练集上选择最优参数
        best_sharpe = -np.inf
        best_params = None
        for params in strategy_params_list:
            sharpe = backtest(params, train_data)['sharpe']
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = params

        # 在测试集上评估最优参数
        oos_result = backtest(best_params, test_data)
        results.append({
            'best_params': best_params,
            'is_sharpe': best_sharpe,
            'oos_sharpe': oos_result['sharpe']
        })

    # PBO-like metric：样本内最优在样本外的表现
    is_vs_oos = pd.DataFrame(results)
    degradation = (is_vs_oos['is_sharpe'] - is_vs_oos['oos_sharpe']).mean()
    print(f"样本内到样本外的夏普衰减: {degradation:.2f}")

    return is_vs_oos
