# @quantlab/output: 5eab4f2d
import numpy as np
import time

def simulate_latency_impact(n_trades=10000, signal_quality=0.55,
                            latency_range=(1e-6, 1e-3)):
    """
    模拟不同延迟水平对HFT策略表现的影响

    参数:
        n_trades: 模拟交易数量
        signal_quality: 信号准确率（>0.5有优势）
        latency_range: (最小延迟, 最大延迟) 单位秒
    """
    results = {}

    for latency in [1e-6, 10e-6, 100e-6, 500e-6, 1e-3, 5e-3]:
        # 模拟：如果延迟为0，成交概率100%；延迟越大，成交概率越低
        fill_probability = max(0, 1.0 - latency / 5e-3)

        # 模拟交易
        np.random.seed(42)
        correct_signals = np.random.random(n_trades) < signal_quality
        got_filled = np.random.random(n_trades) < fill_probability

        # PnL: 正确且成交 -> +1; 错误且成交 -> -1; 未成交 -> 0
        pnl_per_trade = np.where(got_filled,
                                 np.where(correct_signals, 1, -1), 0)
        total_pnl = pnl_per_trade.sum()
        n_filled = got_filled.sum()

        results[latency] = {
            'fill_rate': fill_probability,
            'total_pnl': total_pnl,
            'avg_pnl_per_trade': total_pnl / n_trades,
            'n_filled': n_filled
        }

    print("延迟对HFT策略的影响分析:")
    print("-" * 60)
    print(f"{'延迟(us)':>10} {'成交率':>8} {'成交笔数':>10} {'总PnL':>10} {'单笔PnL':>10}")
    print("-" * 60)
    for latency, r in sorted(results.items()):
        print(f"{latency*1e6:>10.1f} {r['fill_rate']:>8.1%} {r['n_filled']:>10} "
              f"{r['total_pnl']:>10} {r['avg_pnl_per_trade']:>10.4f}")

simulate_latency_impact()
