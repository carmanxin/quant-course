# @quantlab/output: 06d65cd0
def plot_decay_curve(prices: pd.Series,
                     chosen_params: List[Tuple[int, int]],
                     train_window: int = 504,
                     test_window: int = 126,
                     step: int = 63):
    """绘制 Decay 曲线:用训练期的最优参数,在接下来的多个未来窗口上做评估"""
    n = len(prices)
    decay_records = []

    for i, (f, s) in enumerate(chosen_params):
        test_start_idx = i * step + train_window
        if test_start_idx >= n:
            break

        # 在接下来的多个时间距离上评估该参数
        for h in range(1, 6):  # 1 步、2 步、...、5 步
            future_start = test_start_idx + (h - 1) * test_window
            future_end = future_start + test_window
            if future_end > n:
                break

            future_data = prices.iloc[future_start:future_end]
            if len(future_data) < 50:
                continue

            res = double_ma_backtest(future_data, f, s)
            decay_records.append({
                'params_idx': i,
                'horizon_h': h,
                'params': (f, s),
                'sharpe': res['sharpe'],
                'horizon_days': (h - 1) * test_window,
            })

    decay_df = pd.DataFrame(decay_records)
    if decay_df.empty:
        print("无法绘制 Decay 曲线(数据不足)")
        return decay_df

    print("=" * 50)
    print("Decay 曲线:不同时间距离下的 OOS 夏普")
    print("=" * 50)
    grouped = decay_df.groupby('horizon_h')['sharpe'].agg(['mean', 'std', 'count'])
    print(grouped.round(3))

    return decay_df


# 运行 Decay 分析
decay_df = plot_decay_curve(prices, result['chosen_params'])
