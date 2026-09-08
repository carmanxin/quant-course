# @quantlab/output: 5444cfe3
def combinatorial_purged_cv(prices: pd.Series,
                            n_splits: int = 6,
                            n_test_splits: int = 2,
                            purge_gap_days: int = 21,
                            fast_grid: List[int] = None,
                            slow_grid: List[int] = None,
                            fee_rate: float = 0.0003) -> pd.DataFrame:
    """CPCV:所有 N!/(K!(N-K)!) 种测试集组合

    N = 总分组数(默认 6)
    K = 测试组数(默认 2)
    purge_gap = 21 天(对双均线类策略不需要,但展示用法)
    """
    if fast_grid is None:
        fast_grid = [5, 10, 15, 20]
    if slow_grid is None:
        slow_grid = [30, 50, 70, 90]

    param_combos = [(f, s) for f in fast_grid for s in slow_grid if f < s]
    n = len(prices)
    group_size = n // n_splits

    # 生成所有 C(6, 2) = 15 种测试组组合
    from itertools import combinations
    all_combinations = list(combinations(range(n_splits), n_test_splits))

    print(f"CPCV 配置: N={n_splits}, K={n_test_splits}, 总组合数={len(all_combinations)}, "
          f"每组大小={group_size} 天, purge gap={purge_gap_days} 天")

    all_results = []

    for combo_id, test_groups in enumerate(all_combinations):
        train_idx = []
        test_idx = []

        for g in range(n_splits):
            start = g * group_size
            end = (g + 1) * group_size if g < n_splits - 1 else n

            if g in test_groups:
                # 测试组:留出 purge gap
                test_start = start
                test_end = end
                test_idx.extend(range(test_start, test_end))
                # purge gap:从相邻训练组中删除尾部
                if g > 0 and g - 1 not in test_groups:
                    purge_start = max(0, start - purge_gap_days)
                    train_idx.extend([i for i in range(purge_start, start) if i not in set(test_idx)])
            else:
                train_idx.extend(range(start, end))

        if not train_idx or not test_idx:
            continue

        train_data = prices.iloc[train_idx]
        test_data = prices.iloc[test_idx]

        # 在训练集找最优参数
        best_sharpe = -np.inf
        best_params = None
        for f, s in param_combos:
            res = double_ma_backtest(train_data, f, s)
            if res['sharpe'] > best_sharpe:
                best_sharpe = res['sharpe']
                best_params = (f, s)
                best_train_res = res

        # 在测试集评估
        if best_params is not None:
            test_res = double_ma_backtest(test_data, best_params[0], best_params[1])
            all_results.append({
                'combo_id': combo_id,
                'test_groups': test_groups,
                'best_fast': best_params[0],
                'best_slow': best_params[1],
                'train_sharpe': best_train_res['sharpe'],
                'test_sharpe': test_res['sharpe'],
                'test_return': test_res['ann_return'],
                'test_drawdown': test_res['max_drawdown'],
            })

    return pd.DataFrame(all_results)


cpcv_result = combinatorial_purged_cv(prices)
print("\n" + "=" * 60)
print("CPCV 结果汇总")
print("=" * 60)
print(f"成功运行 {len(cpcv_result)} 组 CPCV 组合")
print(f"训练期平均夏普: {cpcv_result['train_sharpe'].mean():.2f}")
print(f"测试期平均夏普: {cpcv_result['test_sharpe'].mean():.2f}")
print(f"夏普衰减率: {(1 - cpcv_result['test_sharpe'].mean() / cpcv_result['train_sharpe'].mean()):.2%}")
print(f"PBO 估约: {(cpcv_result['test_sharpe'] < 0).mean():.2%}")
