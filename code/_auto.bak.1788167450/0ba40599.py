# @quantlab/output: 0ba40599
def evaluate_rl_policy(model, env, n_episodes=10):
    """评估RL策略的表现"""
    episode_rewards = []
    episode_trades = []

    for ep in range(n_episodes):
        obs = env.reset()
        done = False
        total_reward = 0
        n_trades = 0

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            if info.get('position', 0) != 0:
                n_trades = info.get('n_trades', 0)

        episode_rewards.append(total_reward)
        episode_trades.append(n_trades)

    return {
        'avg_reward': np.mean(episode_rewards),
        'std_reward': np.std(episode_rewards),
        'avg_trades': np.mean(episode_trades),
        'sharpe': np.mean(episode_rewards) / np.std(episode_rewards) if np.std(episode_rewards) > 0 else 0
    }

def benchmark_comparison(prices, rl_model):
    """将RL策略与简单基准策略对比"""

    # 基准1：买入持有
    buy_hold_return = (prices[-1] - prices[0]) / prices[0]

    # 基准2：简单移动平均交叉
    sma_short = np.convolve(prices, np.ones(5)/5, mode='valid')
    sma_long = np.convolve(prices, np.ones(20)/20, mode='valid')

    # 对齐长度
    min_len = min(len(sma_short), len(sma_long))
    sma_short = sma_short[-min_len:]
    sma_long = sma_long[-min_len:]

    signals = np.where(sma_short > sma_long, 1, 0)
    sma_returns = np.diff(signals) * np.diff(np.log(prices[-min_len:]))
    sma_return = np.sum(sma_returns[~np.isnan(sma_returns)])

    print("策略对比:")
    print("-" * 40)
    print(f"  买入持有收益:    {buy_hold_return:.2%}")
    print(f"  均线交叉收益:    {sma_return:.2%}")
    if rl_model:
        # RL收益需要从训练结果中获取
        print(f"  RL策略收益:      待训练后评估")

# 执行基准对比（使用模拟价格）
benchmark_comparison(prices, None)
