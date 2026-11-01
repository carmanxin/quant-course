# @quantlab/output: 693ff10f
import gymnasium as gym

class TradingEnv(gym.Env):
    """单资产交易环境 — 自定义 gym.Env 子类的最小骨架"""
    def __init__(self):
        super().__init__()
        # 动作空间: 0=空仓, 1=半仓, 2=全仓
        self.action_space = gym.spaces.Discrete(3)
        # 观察空间: [position, price_return, volatility]
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32
        )

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.position = 0.0
        self.cash = 100000.0
        return np.zeros(3, dtype=np.float32), {}

    def step(self, action):
        reward = 0.0
        terminated = False
        truncated = False
        return np.zeros(3, dtype=np.float32), reward, terminated, truncated, {}

# 演示 API：创建环境、查看空间
import numpy as np
env = TradingEnv()
obs, _ = env.reset()
print("自定义交易环境已创建")
print(f"  动作空间: {env.action_space}  (3 选 1)")
print(f"  观察空间: {env.observation_space.shape}  (3 维)")
print(f"  初始观察: {obs}")
