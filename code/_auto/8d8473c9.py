# @quantlab/output: 8d8473c9
def glosten_milgrom_simulation(v_high: float = 102.0,
                                v_low: float = 98.0,
                                alpha: float = 0.3,
                                delta: float = 0.5,
                                epsilon_b: float = 0.2,
                                epsilon_s: float = 0.2,
                                mu: float = 0.1,
                                n_periods: int = 200,
                                seed: int = 42):
    """
    Glosten-Milgrom(1985) 模型模拟。

    参数:
        v_high: 好消息下的资产价值
        v_low: 坏消息下的资产价值
        alpha: 知情交易者概率
        delta: 好消息概率
        epsilon_b, epsilon_s: 噪声买方和卖方到达率
        mu: 知情交易者到达率
        n_periods: 交易时段数
    """
    np.random.seed(seed)
    v_star = delta * v_high + (1 - delta) * v_low  # 无条件期望价值

    # 随机决定信息事件
    has_info = np.random.rand() < alpha
    good_news = np.random.rand() < delta if has_info else None

    # 确定实际价值
    if has_info and good_news:
        v_true = v_high
    elif has_info and not good_news:
        v_true = v_low
    else:
        v_true = v_star

    # 交易模拟
    bid_quotes = []
    ask_quotes = []
    mid_prices = []
    trades = []

    for t in range(n_periods):
        # 计算到达率
        if has_info:
            if good_news:
                buy_arrival = epsilon_b + mu
                sell_arrival = epsilon_s
            else:
                buy_arrival = epsilon_b
                sell_arrival = epsilon_s + mu
        else:
            buy_arrival = epsilon_b
            sell_arrival = epsilon_s

        # 交易发生
        total_rate = buy_arrival + sell_arrival
        if np.random.rand() < total_rate:
            if np.random.rand() < buy_arrival / total_rate:
                trade_type = 'BUY'
            else:
                trade_type = 'SELL'
        else:
            trade_type = 'NO_TRADE'

        # 做市商更新信念
        if t == 0:
            prior_good = delta
        else:
            prior_good = posterior_good

        # 计算报价（简化条件期望）
        if trade_type == 'BUY':
            likelihood_good = (epsilon_b + mu) / (epsilon_b + epsilon_s + mu)
            likelihood_bad = epsilon_b / (epsilon_b + epsilon_s + mu)
        elif trade_type == 'SELL':
            likelihood_good = epsilon_s / (epsilon_b + epsilon_s + mu)
            likelihood_bad = (epsilon_s + mu) / (epsilon_b + epsilon_s + mu)
        else:
            likelihood_good = 0.5
            likelihood_bad = 0.5

        posterior_good = (prior_good * likelihood_good) / \
            (prior_good * likelihood_good + (1 - prior_good) * likelihood_bad)

        bid = posterior_good * v_low + (1 - posterior_good) * v_low + \
              posterior_good * (v_high - v_low) * 0.0
        ask = posterior_good * v_high + (1 - posterior_good) * v_low

        # 简化价差：基于后验期望
        expected_v = posterior_good * v_high + (1 - posterior_good) * v_low
        spread = 0.5  # 简化固定价差

        bid_quotes.append(expected_v - spread / 2)
        ask_quotes.append(expected_v + spread / 2)
        mid_prices.append(expected_v)
        trades.append(1 if trade_type == 'BUY' else (-1 if trade_type == 'SELL' else 0))

    # 可视化
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    axes[0].fill_between(range(n_periods), bid_quotes, ask_quotes,
                          alpha=0.3, color='gray', label='Bid-Ask Spread')
    axes[0].plot(range(n_periods), mid_prices, 'b-', linewidth=1.2,
                 label='中间价')
    axes[0].axhline(y=v_true, color='green', linestyle='--',
                    label=f'真实价值 = {v_true}')
    axes[0].set_ylabel('价格')
    axes[0].set_title('Glosten-Milgrom 模型：价格发现与价差')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].bar(range(n_periods), trades, color=['green' if t == 1
                else 'red' if t == -1 else 'gray' for t in trades], alpha=0.6)
    axes[1].set_xlabel('交易时段')
    axes[1].set_ylabel('交易方向')
    axes[1].set_title('交易序列（1=买入, -1=卖出, 0=无交易）')
    axes[1].set_ylim(-1.5, 1.5)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    return bid_quotes, ask_quotes, v_true
