# @quantlab/output: 2f51b483
import numpy as np
from scipy.optimize import minimize
from typing import Tuple

class MultivariateHawkes:
    """
    多元 Hawkes 过程用于建模订单簿事件。
    事件类型：买单单、卖单单、买成交、卖成交、买取消、卖取消。
    """

    def __init__(self, n_types: int = 6, decay: float = 50.0):
        """
        参数:
            n_types: 事件类型数量
            decay: 指数衰减参数 β（固定）
        """
        self.n_types = n_types
        self.decay = decay

    def simulate(self,
                 mu: np.ndarray,
                 alpha: np.ndarray,
                 T: float,
                 seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
        """
        模拟多元 Hawkes 过程。

        参数:
            mu: (n_types,) 基线强度
            alpha: (n_types, n_types) 激发矩阵
            T: 模拟时长（秒）
        返回:
            (event_times, event_types)
        """
        np.random.seed(seed)

        # Ogata 的 thinning 算法
        events = []
        t = 0.0

        while t < T:
            # 计算当前总强度
            intensities = mu.copy()
            for ev_time, ev_type in events:
                decay_factor = np.exp(-self.decay * (t - ev_time))
                intensities += alpha[ev_type, :] * decay_factor

            total_intensity = np.sum(intensities)

            # 生成候选事件间隔（使用上界）
            M = total_intensity  # 简化：使用精确强度而非上界
            if M < 1e-10:
                t += 0.001
                continue

            dt = np.random.exponential(1.0 / M)
            t_new = t + dt

            if t_new > T:
                break

            # 接受/拒绝
            intensities_new = mu.copy()
            for ev_time, ev_type in events:
                decay_factor = np.exp(-self.decay * (t_new - ev_time))
                intensities_new += alpha[ev_type, :] * decay_factor

            total_intensity_new = np.sum(intensities_new)

            if np.random.rand() < total_intensity_new / M:
                # 接受事件
                probs = intensities_new / total_intensity_new
                ev_type = np.random.choice(self.n_types, p=probs)
                events.append((t_new, ev_type))

            t = t_new

        event_times = np.array([e[0] for e in events])
        event_types = np.array([e[1] for e in events])

        return event_times, event_types

    def log_likelihood(self,
                       event_times: np.ndarray,
                       event_types: np.ndarray,
                       mu: np.ndarray,
                       alpha: np.ndarray,
                       T: float) -> float:
        """
        计算多元 Hawkes 过程的对数似然函数。
        """
        n_events = len(event_times)
        ll = 0.0

        for i in range(n_events):
            ti = event_times[i]
            ki = event_types[i]

            # 强度
            lam_i = mu[ki]
            for j in range(i):
                tj = event_times[j]
                kj = event_types[j]
                lam_i += alpha[kj, ki] * np.exp(-self.decay * (ti - tj))

            ll += np.log(max(lam_i, 1e-10))

        # 补偿项
        compensator = T * np.sum(mu)
        for i in range(n_events):
            ki = event_types[i]
            ti = event_times[i]
            for k in range(self.n_types):
                compensator -= alpha[ki, k] / self.decay * \
                    (1 - np.exp(-self.decay * (T - ti)))

        ll -= compensator

        return ll

    def fit(self, event_times: np.ndarray,
            event_types: np.ndarray,
            T: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        通过极大似然估计拟合 Hawkes 过程参数。
        """
        n_params = self.n_types + self.n_types ** 2

        def neg_ll(params):
            mu = np.exp(params[:self.n_types])  # 确保正值
            alpha = np.exp(params[self.n_types:]).reshape(
                self.n_types, self.n_types
            )
            return -self.log_likelihood(event_times, event_types, mu, alpha, T)

        # 初始值
        x0 = np.zeros(n_params)

        result = minimize(neg_ll, x0, method='L-BFGS-B',
                          options={'maxiter': 500})

        mu_hat = np.exp(result.x[:self.n_types])
        alpha_hat = np.exp(result.x[self.n_types:]).reshape(
            self.n_types, self.n_types
        )

        return mu_hat, alpha_hat
