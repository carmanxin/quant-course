# @quantlab/output: 4ddcdc67
import numpy as np
import pandas as pd
import time
from numba import jit, njit, prange

# ============================================================
# 任务：计算滚动夏普比率 (rolling 60-day Sharpe ratio)
# 对比三种实现方式的性能
# ============================================================

def benchmark_rolling_sharpe():
    """性能对比：三种实现方式的滚动夏普比率计算"""

    # 生成测试数据
    n_days = 100_000  # 10万日（约400年数据，模拟高频场景）
    n_stocks = 100

    np.random.seed(42)
    returns = np.random.randn(n_days, n_stocks) * 0.02

    window = 60

    results = {}

    # === 方法1：纯Python循环（最慢的方案） ===
    def rolling_sharpe_loop(returns, window):
        n_days, n_stocks = returns.shape
        rolling_sharpe = np.full((n_days - window + 1, n_stocks), np.nan)

        for i in range(n_days - window + 1):
            for j in range(n_stocks):
                window_returns = returns[i:i+window, j]
                mean_ret = np.mean(window_returns)
                std_ret = np.std(window_returns)
                if std_ret > 0:
                    rolling_sharpe[i, j] = mean_ret / std_ret * np.sqrt(252)

        return rolling_sharpe

    start = time.perf_counter()
    _ = rolling_sharpe_loop(returns[:5000, :10], window)  # 只用小数据测试
    results['Python循环 (5K日,10股)'] = time.perf_counter() - start

    # === 方法2：NumPy向量化 ===
    def rolling_sharpe_numpy(returns, window):
        n_days, n_stocks = returns.shape

        # 使用stride技巧创建滚动窗口视图
        from numpy.lib.stride_tricks import sliding_window_view
        windows = sliding_window_view(returns, window, axis=0)  # shape: (n-w+1, n_stocks, w)

        mean_ret = windows.mean(axis=2)
        std_ret = windows.std(axis=2, ddof=1)

        with np.errstate(divide='ignore', invalid='ignore'):
            sharpe = mean_ret / std_ret * np.sqrt(252)
            sharpe[std_ret == 0] = 0

        return sharpe

    start = time.perf_counter()
    _ = rolling_sharpe_numpy(returns, window)
    results['NumPy向量化 (100K日,100股)'] = time.perf_counter() - start

    # === 方法3：Numba JIT编译 ===
    @njit(parallel=True)
    def rolling_sharpe_numba(returns, window):
        n_days, n_stocks = returns.shape
        out_len = n_days - window + 1
        rolling_sharpe = np.zeros((out_len, n_stocks))

        sqrt_252 = np.sqrt(252)

        for j in prange(n_stocks):  # 并行各股票
            for i in range(out_len):
                window_data = returns[i:i+window, j]
                mean_ret = 0.0
                for k in range(window):
                    mean_ret += window_data[k]
                mean_ret /= window

                std_ret = 0.0
                for k in range(window):
                    diff = window_data[k] - mean_ret
                    std_ret += diff * diff
                std_ret = np.sqrt(std_ret / (window - 1))

                if std_ret > 1e-10:
                    rolling_sharpe[i, j] = mean_ret / std_ret * sqrt_252

        return rolling_sharpe

    # 先编译（预热）
    _ = rolling_sharpe_numba(returns[:1000, :5].astype(np.float64), window)

    start = time.perf_counter()
    _ = rolling_sharpe_numba(returns.astype(np.float64), window)
    results['Numba JIT (100K日,100股)'] = time.perf_counter() - start

    # === 方法4：Pandas原生操作 ===
    def rolling_sharpe_pandas(returns, window):
        mean_ret = returns.rolling(window).mean()
        std_ret = returns.rolling(window).std()
        sharpe = mean_ret / std_ret * np.sqrt(252)
        return sharpe.values[window-1:]

    returns_df = pd.DataFrame(returns)
    start = time.perf_counter()
    _ = rolling_sharpe_pandas(returns_df, window)
    results['Pandas滚动窗口 (100K日,100股)'] = time.perf_counter() - start

    # 打印对比结果
    print("=" * 60)
    print(f"滚动夏普比率性能测试 (窗口={window}日)")
    print(f"数据维度: {n_days:,}日 × {n_stocks}股 = {n_days*n_stocks:,} 数据点")
    print("=" * 60)

    for method, elapsed in results.items():
        print(f"  {method:<40} {elapsed:>8.3f} 秒")

    # 速度对比（以最慢为基准）
    print("\n相对速度对比:")
    base_time = results['Python循环 (5K日,10股)'] * (100000/5000) * (100/10)  # 归一化到100K×100
    for method, elapsed in results.items():
        if method == 'Python循环 (5K日,10股)':
            ratio = 1.0
            print(f"  {method:<40} {ratio:>6.0f}x (baseline, 估算)")
        else:
            ratio = base_time / elapsed
            print(f"  {method:<40} {ratio:>6.0f}x")

# 运行测试
# benchmark_rolling_sharpe()
