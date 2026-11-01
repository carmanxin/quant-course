# @quantlab/output: 6825700e
import numpy as np
from scipy.stats import norm


class BlackScholes:
    """Black-Scholes 期权定价与 Greeks 计算"""

    @staticmethod
    def price(S: float, K: float, T: float, r: float,
              sigma: float, option_type: str = 'call') -> float:
        """
        欧式期权定价

        Parameters
        ----------
        S : float
            标的资产现价
        K : float
            行权价格
        T : float
            剩余期限（年）
        r : float
            无风险利率（连续复利）
        sigma : float
            年化波动率
        option_type : str
            'call' 或 'put'
        """
        if T <= 0:
            return max(0, S - K) if option_type == 'call' else max(0, K - S)

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    @staticmethod
    def delta(S: float, K: float, T: float, r: float,
              sigma: float, option_type: str = 'call') -> float:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if option_type == 'call':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    @staticmethod
    def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    @staticmethod
    def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Vega: 波动率每变化1%（0.01），期权价格的变化量"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        return S * np.sqrt(T) * norm.pdf(d1) / 100  # 除以100转换为1%

    @staticmethod
    def theta(S: float, K: float, T: float, r: float,
              sigma: float, option_type: str = 'call') -> float:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        theta_val = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))

        if option_type == 'call':
            theta_val -= r * K * np.exp(-r * T) * norm.cdf(d2)
        else:
            theta_val += r * K * np.exp(-r * T) * norm.cdf(-d2)

        return theta_val / 365  # 转换为每日 theta

    @staticmethod
    def implied_volatility(market_price: float, S: float, K: float,
                           T: float, r: float, option_type: str = 'call',
                           tol: float = 1e-6, max_iter: int = 100) -> float:
        """使用 Newton-Raphson 方法计算隐含波动率"""
        sigma = 0.3  # 初始猜测

        for _ in range(max_iter):
            price = BlackScholes.price(S, K, T, r, sigma, option_type)
            vega = BlackScholes.vega(S, K, T, r, sigma) * 100  # vega 需要反归一化

            diff = price - market_price

            if abs(diff) < tol:
                return sigma

            if abs(vega) < 1e-10:
                break

            sigma = sigma - diff / vega

            # 确保 sigma 在合理范围内
            if sigma <= 0.001:
                sigma = 0.001
            elif sigma > 5.0:
                sigma = 5.0

        return sigma  # 近似的隐含波动率


# 验证 Put-Call Parity
S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20

call_price = BlackScholes.price(S, K, T, r, sigma, 'call')
put_price = BlackScholes.price(S, K, T, r, sigma, 'put')

parity_lhs = call_price - put_price
parity_rhs = S - K * np.exp(-r * T)

print(f"Put-Call Parity 验证:")
print(f"  C - P = {parity_lhs:.6f}")
print(f"  S - Ke^(-rT) = {parity_rhs:.6f}")
print(f"  差异: {abs(parity_lhs - parity_rhs):.2e}")
