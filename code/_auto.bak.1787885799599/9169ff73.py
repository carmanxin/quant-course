# @quantlab/output: 9169ff73
def mc_importance_sampling(S0, K, T, r, sigma, n_paths, option_type='call'):
    """
    重要性采样 —— 将漂移项调整使标的更容易进入实值区域
    """
    # 找到使 S_T 期望接近 K 的漂移调整量
    mu_shift = (np.log(K/S0) - (r - 0.5*sigma**2)*T) / T
    mu_star = r + mu_shift

    Z = np.random.randn(n_paths)
    ST = S0 * np.exp((mu_star - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)

    # 似然比（Radon-Nikodym 导数）
    likelihood_ratio = np.exp(
        -0.5 * (mu_shift*np.sqrt(T)/sigma)**2
        - (mu_shift*np.sqrt(T)/sigma) * Z
    )

    if option_type == 'call':
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)

    price = np.exp(-r * T) * (payoff * likelihood_ratio).mean()
    return price
