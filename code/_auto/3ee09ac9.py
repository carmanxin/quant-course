# @quantlab/output: 3ee09ac9
import numpy as np

def mc_antithetic(S0, K, T, r, sigma, n_paths, option_type='call'):
    """
    对偶变量法 Monte Carlo 期权定价
    每条模拟路径使用配对的正负随机数
    """
    n_pairs = n_paths // 2
    Z = np.random.randn(n_pairs, 2)  # 每对使用同一组随机数

    # 正路径
    ST_pos = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z[:, 0])
    # 对偶路径
    ST_neg = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*(-Z[:, 0]))

    if option_type == 'call':
        payoff_pos = np.maximum(ST_pos - K, 0)
        payoff_neg = np.maximum(ST_neg - K, 0)
    else:
        payoff_pos = np.maximum(K - ST_pos, 0)
        payoff_neg = np.maximum(K - ST_neg, 0)

    # 每对取平均
    payoff_avg = (payoff_pos + payoff_neg) / 2
    price = np.exp(-r * T) * payoff_avg.mean()
    se = payoff_avg.std() / np.sqrt(n_pairs)

    return price, se

# 对比标准MC与对偶变量法
price_av, se_av = mc_antithetic(100, 100, 1.0, 0.03, 0.20, 100000, 'call')
print(f"对偶变量法: {price_av:.6f} ± {1.96*se_av:.6f} (95% CI)")
