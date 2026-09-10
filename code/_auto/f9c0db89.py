# @quantlab/output: f9c0db89
def run_backtest(strategy, data, start_date, end_date):
    """
    完整的回测主循环，模拟逐日交易流程
    """
    # 初始化
    capital = 1_000_000
    positions = {}  # symbol -> shares
    equity_curve = []

    # 按日期遍历
    trading_dates = data[start_date:end_date].index
    prev_positions = {}

    for i, date in enumerate(trading_dates):
        # Step 1: 获取当日数据（仅使用截止当日的已知数据）
        historical_data = data.loc[:date]
        current_prices = data.loc[date, 'Close']

        # Step 2: 计算当前组合市值
        portfolio_value = capital
        for sym, shares in positions.items():
            portfolio_value += shares * current_prices[sym]

        # Step 3: 生成信号（关键：只用历史数据，不用未来数据）
        signals = strategy.predict(historical_data)

        # Step 4: 计算目标持仓（组合优化 + 风控约束）
        target_weights = optimize_portfolio(
            signals,
            historical_data.pct_change().dropna().cov(),
            max_weight=0.1,
            max_turnover=0.3
        )

        # Step 5: 执行交易（含成本）
        for sym, target_w in target_weights.items():
            target_value = portfolio_value * target_w
            current_value = positions.get(sym, 0) * current_prices[sym]
            trade_value = target_value - current_value

            # 买入/卖出
            trade_shares = int(trade_value / current_prices[sym])
            commission = abs(trade_shares * current_prices[sym]) * 0.0003
            slippage = abs(trade_shares * current_prices[sym]) * 0.0002

            capital -= (trade_value + commission + slippage)
            positions[sym] = positions.get(sym, 0) + trade_shares

        # Step 6: 记录净值
        final_value = capital + sum(
            positions.get(sym, 0) * current_prices[sym] for sym in current_prices.index
        )
        equity_curve.append({'date': date, 'equity': final_value})

    return pd.DataFrame(equity_curve).set_index('date')
