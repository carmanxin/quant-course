# @quantlab/output: 7e6b08e4
def pairs_screening(price_df, n_top=10):
    """
    从股票池中筛选最优的交易对

    步骤：
    1. 计算所有配对的相关性和协整p值
    2. 筛选协整显著且半衰期合理的配对
    3. 按夏普比率排序，选择前N对
    """
    stocks = price_df.columns
    pairs_results = []

    for i, stock_a in enumerate(stocks):
        for stock_b in stocks[i+1:]:
            pa = price_df[stock_a].dropna()
            pb = price_df[stock_b].dropna()

            # 对齐时间
            common_idx = pa.index.intersection(pb.index)
            if len(common_idx) < 252:  # 至少一年数据
                continue

            pa = pa[common_idx]
            pb = pb[common_idx]

            # 相关性
            corr = pa.pct_change().corr(pb.pct_change())

            # 协整检验
            _, p_value, _ = coint(pa, pb)

            # 如果通过初筛，做完整的回测
            if p_value < 0.1 and corr > 0.6:
                trader = PairsTrader()
                signals, info = trader.generate_signals(pa, pb)

                if info['half_life'] < 60:  # 半衰期在合理范围
                    rets_a = pa.pct_change()
                    rets_b = pb.pct_change()
                    spread_rets = signals.shift(1) * (rets_a - info.get('hedge_ratio', 1) * rets_b)
                    sharpe = spread_rets.mean() / spread_rets.std() * np.sqrt(252)

                    pairs_results.append({
                        'stock_a': stock_a, 'stock_b': stock_b,
                        'correlation': corr,
                        'coint_pvalue': p_value,
                        'half_life': info['half_life'],
                        'sharpe': sharpe
                    })

    return pd.DataFrame(pairs_results).sort_values('sharpe', ascending=False).head(n_top)
