# @quantlab/output: c6786263
def backtest_with_costs(strategy, data, cost_model):
    """
    带完整成本模型的回测循环
    """
    capital = 1_000_000
    positions = {}
    equity_curve = []
    cost_log = []

    for date, row in data.iterrows():
        # 策略生成目标持仓
        target_positions = strategy.predict(row, positions)

        # 计算所需交易
        current_symbols = set(positions.keys()) | set(target_positions.keys())
        daily_cost = 0

        for sym in current_symbols:
            target_shares = target_positions.get(sym, 0)
            current_shares = positions.get(sym, 0)
            diff = target_shares - current_shares

            if diff != 0:
                side = 'buy' if diff > 0 else 'sell'
                cost_info = cost_model.calculate_cost(
                    price=row['Close', sym],
                    shares=abs(diff),
                    side=side,
                    avg_daily_volume=row.get(('Volume', sym), None)
                )
                daily_cost += cost_info['total_cost']
                cost_log.append({**cost_info, 'date': date, 'symbol': sym})

        # 执行交易并扣除成本
        for sym in current_symbols:
            target_shares = target_positions.get(sym, 0)
            current_shares = positions.get(sym, 0)
            diff = target_shares - current_shares

            if diff != 0:
                capital -= diff * row['Close', sym]  # 支付买入/收入卖出

        capital -= daily_cost  # 扣除交易成本
        positions = {k: v for k, v in target_positions.items() if v != 0}

        # 记录净值
        total_value = capital + sum(
            positions.get(sym, 0) * row['Close', sym]
            for sym in positions
        )
        equity_curve.append({'date': date, 'equity': total_value})

    return pd.DataFrame(equity_curve).set_index('date'), pd.DataFrame(cost_log)
