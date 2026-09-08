
# ===== 演示：环境自检 + 随机策略基线 =====
np.random.seed(42)
n_days = 500
# 模拟带趋势和波动聚类的价格序列
returns = np.random.randn(n_days) * 0.01
returns[100:200] += 0.003   # 上行趋势
returns[300:400] -= 0.002   # 下行趋势
prices = 100 * np.exp(np.cumsum(returns))

env = TradingEnvironment(prices, window_size=20)
print("=== RL 交易环境就绪 ===")
print(f"  价格序列长度    : {len(prices)}")
print(f"  价格范围        : [{prices.min():.1f}, {prices.max():.1f}]")
print(f"  动作空间        : {env.action_space}  (0=空仓, 1=半仓, 2=全仓)")
print(f"  观测空间维度    : {env.observation_space.shape[0]} "
      f"(持仓1 + 收益窗口{env.window_size} + 波动率1 + 趋势1)")

obs, _ = env.reset(seed=0)
print(f"\n  reset 后观测形状  : {obs.shape}, dtype={obs.dtype}")
step_ret = env.step(2)
print(f"  step(2) 返回元素 : {len(step_ret)} 个 -> (obs, reward, terminated, truncated, info)")
print(f"  info 字段        : {list(step_ret[4].keys())}")


def run_episode(policy, seed=0):
    """跑完整一轮 episode，返回 (总PnL, 交易次数, 步数)"""
    o, _ = env.reset(seed=seed)
    done = False
    steps = 0
    while not done:
        a = policy(o)
        o, r, term, trunc, info = env.step(a)
        done = term or trunc
        steps += 1
    return info['total_pnl'], info['n_trades'], steps


# 基线 1：随机策略
rng = np.random.default_rng(7)
random_pnl, random_trades, random_steps = run_episode(lambda o: int(rng.integers(0, 3)))

# 基线 2：始终全仓（近似买入持有）
always_pnl, always_trades, always_steps = run_episode(lambda o: 2)

# 基准：买入持有（无成本）
bh = prices[-1] / prices[env.window_size] - 1

print("\n=== 基线对比（单轮 episode，含 0.1% 单边成本）===")
print(f"  {'策略':<12}{'总收益':>12}{'交易次数':>10}{'步数':>8}")
print(f"  {'随机策略':<12}{random_pnl * 100:>11.2f}%{random_trades:>10}{random_steps:>8}")
print(f"  {'始终全仓':<12}{always_pnl * 100:>11.2f}%{always_trades:>10}{always_steps:>8}")
print(f"  {'买入持有(无成本)':<12}{bh * 100:>11.2f}%{1:>10}{len(prices) - env.window_size:>8}")

print("\n=== 观察 ===")
print("  · 随机策略频繁换手，交易成本侵蚀收益，通常显著跑输买入持有")
print("  · 始终全仓≈买入持有，差额即累计交易成本")
print("  · PPO 要超越上述基线才有训练价值——这正是 RL 交易的现实门槛")

try:
    import stable_baselines3  # noqa: F401
    print("\n  stable-baselines3 已安装，可调用 train_rl_trader(prices) 训练 PPO")
except ImportError:
    print("\n  提示: train_rl_trader(prices) 需先 pip install stable-baselines3")
    print("        （本页预计算结果由上述不依赖 SB3 的环境自检 + 基线对比生成）")
