# @quantlab/output: 39e50ba3
import numpy as np
import time

np.random.seed(42)
returns = np.random.randn(1_000_000)   # 100 万条收益率

# ===== 方法1：Python 循环，逐元素累加 =====
start = time.perf_counter()
total = 0.0
for r in returns:                      # 每次迭代都产出 numpy 标量，开销很大
    total += r
mean_loop = total / len(returns)

sq_sum = 0.0
for r in returns:                      # 第二遍：算方差
    sq_sum += (r - mean_loop) ** 2
std_loop = (sq_sum / len(returns)) ** 0.5
sharpe_loop = mean_loop / std_loop
t_loop = time.perf_counter() - start

# ===== 方法2：NumPy 向量化 =====
start = time.perf_counter()
sharpe_np = returns.mean() / returns.std()
t_np = time.perf_counter() - start

print(f"Python 循环  : sharpe={sharpe_loop:+.8f}   耗时 {t_loop*1000:8.1f} ms")
print(f"NumPy 向量化 : sharpe={sharpe_np:+.8f}   耗时 {t_np*1000:8.2f} ms")
print(f"加速倍数: {t_loop / t_np:.0f}x     两者差异: {abs(sharpe_loop - sharpe_np):.2e}")
print("\n注: 此处是单期(未年化)的均值/标准差; 数据为纯随机正态, 理论值≈0, 结果接近 0 属正常。")
