# @quantlab/output: 4d36d716
import numpy as np
import gym
from gym import spaces
from collections import deque
from typing import Tuple, Optional

class TradingEnvironment(gym.Env):
    """
    单资产RL交易环境

    状态: [持仓, 价格变化率(N窗口), 波动率, 技术指标...]
    动作: 0=空仓, 1=持有(离散) 或 [-1, 1]连续仓位
    奖励: 每步的PnL变化 - 交易成本
    """

    def __init__(self, prices, window_size=20,
                 transaction_cost_pct=0.001,
                 reward_scaling=100.0):
        super().__init__()

        self.prices = np.array(prices, dtype=np.float32)
        self.window_size = window_size
        self.transaction_cost = transaction_cost_pct
        self.reward_scaling = reward_scaling

        # 动作空间：离散(0=空仓, 1=半仓, 2=全仓)
        self.action_space = spaces.Discrete(3)

        # 观察空间：持仓 + 价格特征
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(1 + window_size + 2,),  # 持仓 + 价格窗口 + 波动率 + 趋势
            dtype=np.float32
        )

        self.reset()

    def _get_observation(self) -> np.ndarray:
        """构建当前状态表示"""
        # 价格窗口特征
        price_window = self.prices[self.current_step - self.window_size + 1:
                                   self.current_step + 1]
        returns = np.diff(price_window) / price_window[:-1]

        # 填充到fixed length
        if len(returns) < self.window_size:
            returns = np.pad(returns, (self.window_size - len(returns), 0),
                           mode='constant')

        # 技术特征
        recent_prices = self.prices[max(0, self.current_step - self.window_size):
                                     self.current_step + 1]
        volatility = np.std(np.diff(recent_prices) / recent_prices[:-1]) if len(recent_prices) > 1 else 0

        # 趋势强度（当前价格相对于移动平均）
        if len(recent_prices) >= 5:
            sma = np.mean(recent_prices[-5:])
            trend = (recent_prices[-1] - sma) / sma
        else:
            trend = 0.0

        # 组合状态向量
        obs = np.array([
            self.position,        # 当前持仓 (0, 0.5, 1.0)
            *returns[-self.window_size:],  # 价格收益率序列
            volatility,           # 波动率
            trend,                # 趋势
        ], dtype=np.float32)

        return obs

    def reset(self) -> np.ndarray:
        """重置环境到初始状态"""
        self.current_step = self.window_size
        self.position = 0.0
        self.entry_price = 0.0
        self.total_pnl = 0.0
        self.trades = []

        return self._get_observation()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """执行一步交易"""
        # 将离散动作映射为持仓
        target_position = np.array([0.0, 0.5, 1.0])[action]

        current_price = self.prices[self.current_step]

        # 计算奖励（PnL变化）
        reward = 0.0

        if self.position > 0 and target_position == 0:
            # 卖出（全部平仓）
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            reward = pnl_pct * self.position - self.transaction_cost
            self.total_pnl += reward
            self.position = 0.0
            self.trades.append(('SELL', current_price, reward))

        elif self.position == 0 and target_position > 0:
            # 买入（建仓）
            self.position = target_position
            self.entry_price = current_price
            reward = -self.transaction_cost  # 只扣手续费（价格尚未变化）
            self.trades.append(('BUY', current_price, reward))

        elif self.position > 0 and target_position > 0:
            # 持有：按仓位计算价格变动
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            reward = pnl_pct * self.position
            # 更新入场价（按新仓位）
            self.entry_price = current_price
        else:
            # 空仓观望
            reward = 0.0

        reward *= self.reward_scaling

        # 前进时间
        self.current_step += 1
        done = self.current_step >= len(self.prices) - 1

        # 终止时平仓
        if done and self.position > 0:
            final_pnl = (current_price - self.entry_price) / self.entry_price * self.position
            reward += (final_pnl - self.transaction_cost) * self.reward_scaling
            self.total_pnl += final_pnl - self.transaction_cost

        obs = self._get_observation() if not done else np.zeros_like(self._get_observation())

        info = {
            'total_pnl': self.total_pnl,
            'position': self.position,
            'current_price': current_price,
            'n_trades': len(self.trades)
        }

        return obs, reward, done, info

    def render(self, mode='human'):
        pass

# ===== 使用PPO训练 =====

def train_rl_trader(prices, n_episodes=100):
    """
    使用Stable-Baselines3 PPO训练交易Agent

    需要安装: pip install stable-baselines3
    """
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv
        from stable_baselines3.common.callbacks import EvalCallback
    except ImportError:
        print("需要安装 stable-baselines3: pip install stable-baselines3")
        return None

    # 创建环境
    env = TradingEnvironment(prices, window_size=20)
    env = DummyVecEnv([lambda: env])

    # 创建PPO模型
    model = PPO(
        'MlpPolicy',
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,  # 熵正则化系数（鼓励探索）
        verbose=1,
    )

    # 训练
    model.learn(total_timesteps=n_episodes * 1000)

    return model, env

# 生成模拟价格数据
np.random.seed(42)
n_days = 500
# 模拟带趋势和波动聚类的价格序列
returns = np.random.randn(n_days) * 0.01
# 加入一些趋势
returns[100:200] += 0.003  # 上行趋势
returns[300:400] -= 0.002  # 下行趋势
prices = 100 * np.exp(np.cumsum(returns))

print("RL交易环境就绪")
print(f"  价格序列长度: {len(prices)}")
print(f"  价格范围: [{prices.min():.1f}, {prices.max():.1f}]")
print(f"  观测空间维度: {TradingEnvironment(prices).observation_space.shape[0]}")
print(f"\n  提示: 运行 train_rl_trader(prices) 来训练PPO模型")
