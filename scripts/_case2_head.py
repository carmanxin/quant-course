import numpy as np
import gymnasium as gym
from gymnasium import spaces
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
    def reset(self, *, seed=None, options=None) -> np.ndarray:
        """重置环境到初始状态"""
        super().reset(seed=seed)
        self.current_step = self.window_size
        self.position = 0.0
        self.entry_price = 0.0
        self.total_pnl = 0.0
        self.trades = []
        return self._get_observation(), {}
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """执行一步交易

        会计口径：
          · reward（奖励塑形）= 本步价格变动 × 持仓 - 本步交易成本
          · total_pnl（真实盈亏）= 建仓→平仓的持仓期收益 × 平均仓位 - 累计成本
        两者刻意分开：前者给 RL 密集反馈，后者给人类可读的真实业绩。
        """
        # 将离散动作映射为持仓
        target_position = np.array([0.0, 0.5, 1.0])[action]
        current_price = self.prices[self.current_step]
        prev_price = self.prices[self.current_step - 1] if self.current_step > 0 else current_price
        step_ret = (current_price - prev_price) / prev_price

        # 本步的奖励 = 价格变动带来的浮盈（按当前持仓计价）
        reward = step_ret * self.position
        cost = 0.0

        if self.position > 0 and target_position == 0:
            # 卖出（全部平仓）
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            realized = pnl_pct * self.position - self.transaction_cost
            self.total_pnl += realized
            cost = self.transaction_cost
            self.trades.append(('SELL', current_price, realized))
            self.position = 0.0
            self.entry_price = 0.0
        elif self.position == 0 and target_position > 0:
            # 买入（建仓）
            self.position = target_position
            self.entry_price = current_price
            self.total_pnl -= self.transaction_cost
            cost = self.transaction_cost
            self.trades.append(('BUY', current_price, -self.transaction_cost))
        elif self.position > 0 and abs(target_position - self.position) > 1e-9:
            # 加减仓：先结算旧仓位，再按新仓位重新建仓
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            realized = pnl_pct * self.position
            self.total_pnl += realized
            self.trades.append(('REBALANCE', current_price, realized))
            self.position = target_position
            self.entry_price = current_price
        # 其余情况：持仓不变，纯持有，不做任何结算

        reward = (reward - cost) * self.reward_scaling

        # 前进时间
        self.current_step += 1
        terminated = self.current_step >= len(self.prices) - 1
        truncated = False

        # 终止时强制平仓（注意：current_price 是推进前的价格，此处要用推进后的价格）
        if terminated and self.position > 0:
            exit_price = self.prices[min(self.current_step, len(self.prices) - 1)]
            final_pnl = (exit_price - self.entry_price) / self.entry_price * self.position
            self.total_pnl += final_pnl - self.transaction_cost
            reward += (final_pnl - self.transaction_cost) * self.reward_scaling
            self.trades.append(('SELL', exit_price, final_pnl - self.transaction_cost))
            self.position = 0.0
            self.entry_price = 0.0

        obs = self._get_observation() if not terminated else np.zeros_like(self._get_observation())
        info = {
            'total_pnl': self.total_pnl,
            'position': self.position,
            'current_price': current_price,
            'n_trades': len(self.trades)
        }
        return obs, reward, terminated, truncated, info

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
