# @quantlab/output: 9fd26d69
def queue_position_model(lob_snapshots: list,
                          target_price: float,
                          max_horizon: int = 100) -> dict:
    """
    基于历史LOB快照估计队列位置的成交概率。

    参数:
        lob_snapshots: LOB快照列表，每个包含 bid_sizes, ask_sizes 等
        target_price: 目标挂单价位
        max_horizon: 最大预测时间步
    返回:
        包含成交概率曲线的字典
    """
    # 简化模拟：假设Poisson过程的订单消耗

    n_simulations = 1000
    fill_times = []

    for sim in range(n_simulations):
        queue_size = np.random.randint(100, 10000)  # 初始队列量
        position = np.random.randint(1, max(10, queue_size // 10))

        # 模拟订单消耗过程
        time = 0
        filled = False

        while time < max_horizon and not filled:
            # 市价单到达率（简化模型）
            market_order_arrival = np.random.poisson(0.3)
            if market_order_arrival > 0:
                executed_volume = np.random.exponential(500)
                queue_size -= executed_volume
                position -= executed_volume

                if position <= 0:
                    filled = True
                    fill_times.append(time)

            # 取消率
            if np.random.rand() < 0.02:
                cancelled = np.random.exponential(200)
                if position > queue_size * 0.5:  # 在队尾附近
                    queue_size -= cancelled

            time += 1

    # 成交概率曲线
    horizon_range = range(1, max_horizon + 1)
    fill_probs = [np.mean(np.array(fill_times) <= h) for h in horizon_range]

    # 拟合指数衰减曲线
    from scipy.optimize import curve_fit

    def exp_decay(t, a, b):
        return a * (1 - np.exp(-b * t))

    try:
        popt, _ = curve_fit(exp_decay, list(horizon_range), fill_probs,
                            p0=[1.0, 0.1])
    except:
        popt = [1.0, 0.1]

    return {
        'fill_times': fill_times,
        'fill_probs': fill_probs,
        'mean_fill_time': np.mean(fill_times) if fill_times else max_horizon,
        'median_fill_time': np.median(fill_times) if fill_times else max_horizon,
        'fit_params': popt
    }
