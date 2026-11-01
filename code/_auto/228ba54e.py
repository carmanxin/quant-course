# @quantlab/output: 228ba54e
import numpy as np
import matplotlib.pyplot as plt

def kyle_model_simulation(v_true: float = 100.0,
                           sigma_u: float = 10.0,
                           n_auctions: int = 10,
                           seed: int = 42):
    """
    模拟 Kyle(1985) 连续拍卖过程。

    参数:
        v_true: 资产的真实价值
        sigma_u: 噪声交易者订单的标准差
        n_auctions: 拍卖轮数
    """
    np.random.seed(seed)
    p0 = v_true * (1 + np.random.randn() * 0.02)  # 初始价格有微小偏差
    sigma_v = 2.0  # 初始价值不确定性

    prices = [p0]
    lambda_vals = []
    informed_orders = []
    noise_orders = []
    info_remaining = [sigma_v]

    for t in range(1, n_auctions + 1):
        # Kyle's lambda
        lam = 0.5 * np.sqrt(sigma_v / (sigma_u ** 2))
        lambda_vals.append(lam)

        # 知情者最优订单
        beta = np.sqrt(sigma_u ** 2 / sigma_v)
        x = beta * (v_true - prices[-1])
        informed_orders.append(x)

        # 噪声订单
        u = np.random.normal(0, sigma_u)
        noise_orders.append(u)

        # 总订单流
        y = x + u

        # 做市商定价
        p_new = prices[-1] + lam * y
        prices.append(p_new)

        # 更新不确定性（信息逐渐被吸收）
        sigma_v = sigma_v / 2
        info_remaining.append(sigma_v)

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].plot(range(len(prices)), prices, 'b-o', markersize=6)
    axes[0, 0].axhline(y=v_true, color='green', linestyle='--',
                       label=f'真实价值 = {v_true}')
    axes[0, 0].set_xlabel('拍卖轮次')
    axes[0, 0].set_ylabel('价格')
    axes[0, 0].set_title('Kyle 模型：价格发现过程')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].bar(range(1, n_auctions + 1), lambda_vals, color='steelblue')
    axes[0, 1].set_xlabel('拍卖轮次')
    axes[0, 1].set_ylabel("Kyle's Lambda")
    axes[0, 1].set_title('价格冲击系数变化')
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].bar(range(1, n_auctions + 1), informed_orders,
                   label='知情者订单', alpha=0.7)
    axes[1, 0].bar(range(1, n_auctions + 1), noise_orders,
                   label='噪声订单', alpha=0.7)
    axes[1, 0].set_xlabel('拍卖轮次')
    axes[1, 0].set_ylabel('订单量')
    axes[1, 0].set_title('订单分解')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(range(n_auctions + 1), info_remaining, 'r-o', markersize=6)
    axes[1, 1].set_xlabel('拍卖轮次')
    axes[1, 1].set_ylabel('剩余信息不确定性')
    axes[1, 1].set_title('信息被价格吸收的速度')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    return prices, lambda_vals
