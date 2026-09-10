# @quantlab/output: 39e79665
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def analyze_lob_statistics(bid_prices: np.ndarray,
                            bid_sizes: np.ndarray,
                            ask_prices: np.ndarray,
                            ask_sizes: np.ndarray) -> dict:
    """
    分析限价订单簿的关键统计特性。

    参数:
        bid_prices: (T, K) 数组，T个时刻、K个档位的买价
        bid_sizes: (T, K) 数组，对应挂单量
        ask_prices: (T, K) 数组，卖价
        ask_sizes: (T, K) 数组，卖盘挂单量
    返回:
        统计特性字典
    """
    T, K = bid_prices.shape

    # 1. 价差统计
    spread = ask_prices[:, 0] - bid_prices[:, 0]
    mid_price = (ask_prices[:, 0] + bid_prices[:, 0]) / 2
    relative_spread = spread / mid_price * 10000  # bps

    # 2. 订单簿不平衡
    total_bid = np.sum(bid_sizes, axis=1)
    total_ask = np.sum(ask_sizes, axis=1)
    book_imbalance = (total_bid - total_ask) / (total_bid + total_ask + 1e-10)

    # 3. 深度加权平均价格
    dwap_bid = np.sum(bid_prices * bid_sizes, axis=1) / (total_bid + 1e-10)
    dwap_ask = np.sum(ask_prices * ask_sizes, axis=1) / (total_ask + 1e-10)

    # 4. 价格变动的离散性
    price_changes = np.diff(mid_price)
    tick_size = np.median(np.abs(np.diff(np.unique(np.round(mid_price, 2)))))

    stats_summary = {
        'spread_mean': np.mean(spread),
        'spread_median': np.median(spread),
        'relative_spread_bps_mean': np.mean(relative_spread),
        'book_imbalance_mean': np.mean(book_imbalance),
        'book_imbalance_autocorr': np.corrcoef(
            book_imbalance[:-1], book_imbalance[1:]
        )[0, 1],
        'price_changes_std': np.std(price_changes),
        'tick_size_estimate': tick_size
    }

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 价差分布
    axes[0, 0].hist(spread, bins=50, color='steelblue', edgecolor='white',
                    alpha=0.8, density=True)
    axes[0, 0].axvline(x=np.mean(spread), color='red', linestyle='--',
                       label=f'均值 = {np.mean(spread):.4f}')
    axes[0, 0].set_xlabel('买卖价差')
    axes[0, 0].set_ylabel('频率')
    axes[0, 0].set_title('价差分布')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 订单簿平均形状
    avg_bid_depth = np.mean(bid_sizes, axis=0)
    avg_ask_depth = np.mean(ask_sizes, axis=0)

    levels = np.arange(1, K + 1)
    axes[0, 1].bar(-levels, avg_bid_depth[::-1], color='green', alpha=0.6,
                   label='买盘')
    axes[0, 1].bar(levels, avg_ask_depth, color='red', alpha=0.6,
                   label='卖盘')
    axes[0, 1].set_xlabel('档位（负=买, 正=卖）')
    axes[0, 1].set_ylabel('平均挂单量')
    axes[0, 1].set_title('订单簿平均形状')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 订单簿不平衡的时序
    axes[1, 0].plot(book_imbalance, 'b-', linewidth=0.8)
    axes[1, 0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('时间')
    axes[1, 0].set_ylabel('订单簿不平衡')
    axes[1, 0].set_title('订单簿不平衡时序')
    axes[1, 0].grid(True, alpha=0.3)

    # 不平衡自相关
    lags = range(1, 51)
    autocorrs = [np.corrcoef(book_imbalance[:-lag], book_imbalance[lag:])[0, 1]
                 for lag in lags]
    axes[1, 1].bar(lags, autocorrs, width=0.8, color='steelblue')
    axes[1, 1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[1, 1].set_xlabel('滞后阶数')
    axes[1, 1].set_ylabel('自相关系数')
    axes[1, 1].set_title('订单簿不平衡自相关函数')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    return stats_summary
