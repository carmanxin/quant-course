# @quantlab/output: 1b7cb6c8
import numpy as np
import matplotlib.pyplot as plt

def simulate_kelly(win_rate=0.55, win_loss_ratio=1.5, n_trades=200, n_paths=100, fractions=[0.05, 0.1, 0.2, 0.25, 0.4, 0.6, 0.8]):
    """
    模拟不同投注比例下的资金增长轨迹
    注意: n_trades=200 —— 复利下 1000 笔会让终值爆炸到 1e19 量级,
    既不可读也不现实(实盘很少连续同参数交易 1000 次), 200 笔足以看出拐点。
    """
    results = {}

    for f in fractions:
        all_paths = []
        for path in range(n_paths):
            capital = 1.0
            for _ in range(n_trades):
                if np.random.random() < win_rate:
                    # 盈利
                    capital *= (1 + f * win_loss_ratio)
                else:
                    # 亏损
                    capital *= (1 - f * 1.0)  # 亏损100%的投入
                if capital < 0.001:  # 爆仓
                    capital = 0.001
                    break
            all_paths.append(capital)
        results[f] = {
            'median': np.median(all_paths),
            'mean': np.mean(all_paths),
            'p5': np.percentile(all_paths, 5),
            'p95': np.percentile(all_paths, 95),
            'bankruptcy_rate': np.mean(np.array(all_paths) < 0.01)
        }

    return results

# 计算理论凯利比例
kelly_f = round(0.55 - (1 - 0.55) / 1.5, 2)  # = 0.25
print(f"理论凯利比例: {kelly_f:.2%}")

# 大数用科学计数法, 否则保留一位小数
def fmt(x):
    return f"{x:.2e}" if x >= 1e5 or (0 < x < 1e-3) else f"{x:.1f}"

# 模拟验证
n_trades = 200
results = simulate_kelly(n_trades=n_trades)

print(f"\n{'比例':>6} {'中位数':>10} {'均值':>10} {'单笔g':>8} {'爆仓率':>8}")
print("-" * 46)
for f, stats in results.items():
    # g = 每笔的几何增长率, 是可跨 n_trades 比较的"真实速度";
    # 均值被少数暴富路径拉高, 中位数才是典型路径
    g = stats['median'] ** (1 / n_trades) - 1
    tag = "  <- Kelly" if abs(f - kelly_f) < 1e-9 else ""
    print(f"{f:>6.0%} {fmt(stats['median']):>10} {fmt(stats['mean']):>10} "
          f"{g:>8.2%} {stats['bankruptcy_rate']:>8.1%}{tag}")

# 绘制终端资金分布
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

fractions = list(results.keys())
medians = [r['median'] for r in results.values()]
bankruptcies = [r['bankruptcy_rate'] for r in results.values()]

axes[0].bar([f'{f:.0%}' for f in fractions], medians, color='steelblue', edgecolor='white')
axes[0].set_yscale('log')  # 各比例终值相差数个量级, 线性轴会挤成一片
axes[0].axvline(x=list(fractions).index(kelly_f), color='red', linestyle='--', label=f'Kelly={kelly_f:.0%}')
axes[0].set_title('不同投注比例下的中位数终值 (对数轴)')
axes[0].set_ylabel('终值倍数')
axes[0].legend()

axes[1].bar([f'{f:.0%}' for f in fractions], bankruptcies, color='coral', edgecolor='white')
axes[1].set_title('不同投注比例下的爆仓率')
axes[1].set_ylabel('爆仓概率')

plt.tight_layout()
plt.show()
