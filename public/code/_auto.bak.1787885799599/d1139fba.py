# @quantlab/output: d1139fba
import numpy as np
import matplotlib.pyplot as plt

def simulate_kelly(win_rate=0.55, win_loss_ratio=1.5, n_trades=1000, n_paths=100, fractions=[0.05, 0.1, 0.2, 0.4, 0.6, 0.8]):
    """
    模拟不同投注比例下的资金增长轨迹
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

# 模拟验证
results = simulate_kelly()
for f, stats in results.items():
    print(f"投注比例={f:.0%}: 中位数={stats['median']:.1f}x, "
          f"均值={stats['mean']:.1f}x, 爆仓率={stats['bankruptcy_rate']:.1%}")

# 绘制终端资金分布
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

fractions = list(results.keys())
medians = [r['median'] for r in results.values()]
bankruptcies = [r['bankruptcy_rate'] for r in results.values()]

axes[0].bar([f'{f:.0%}' for f in fractions], medians, color='steelblue', edgecolor='white')
axes[0].axvline(x=list(fractions).index(kelly_f), color='red', linestyle='--', label=f'Kelly={kelly_f:.0%}')
axes[0].set_title('不同投注比例下的中位数终值')
axes[0].set_ylabel('终值倍数')
axes[0].legend()

axes[1].bar([f'{f:.0%}' for f in fractions], bankruptcies, color='coral', edgecolor='white')
axes[1].set_title('不同投注比例下的爆仓率')
axes[1].set_ylabel('爆仓概率')

plt.tight_layout()
plt.show()
