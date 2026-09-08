# @quantlab/output: ea580041
def analyze_lambda_impact(X: float = 10000,
                           T: float = 60,
                           N: int = 100,
                           sigma: float = 0.3,
                           gamma: float = 2.5e-7,
                           eta: float = 2.5e-6):
    """
    分析不同风险厌恶参数下的最优执行轨迹。
    """
    lambda_values = [0.0, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    t = np.linspace(0, T, N + 1)

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for i, lam in enumerate(lambda_values):
        x = ac_optimal_trajectory(X, T, N, sigma, gamma, eta, lam)

        # 执行速率
        v = -np.diff(x) / (T / N)

        ax1 = axes[i]
        ax2 = ax1.twinx()

        line1, = ax1.plot(t, x, 'b-', linewidth=2, label='剩余头寸')
        line2, = ax2.plot(t[:-1], v, 'r--', linewidth=1.5, alpha=0.7,
                          label='执行速率')

        # 等速执行参考线
        vwap_x = X * (1 - t / T)
        ax1.plot(t, vwap_x, 'gray', linewidth=1, alpha=0.5,
                 linestyle=':', label='VWAP (λ=0)')

        ax1.set_xlabel('时间 (分钟)')
        ax1.set_ylabel('剩余头寸', color='blue')
        ax2.set_ylabel('执行速率', color='red')
        ax1.set_title(f'λ = {lam:.0e}')
        ax1.grid(True, alpha=0.3)

        # 添加图例
        lines = [line1, line2]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')

    plt.suptitle('风险厌恶参数 λ 对最优执行策略的影响', fontsize=14, y=1.01)
    plt.tight_layout()
    plt.show()
