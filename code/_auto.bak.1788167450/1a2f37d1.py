# @quantlab/output: 1a2f37d1
import pandas as pd
import numpy as np
import time

def pandas_optimization_demo():
    """
    展示Pandas中常见的性能优化技巧
    """
    # 准备测试数据
    n = 1_000_000
    df = pd.DataFrame({
        'A': np.random.randn(n),
        'B': np.random.randn(n),
        'C': np.random.choice(['X', 'Y', 'Z'], n),
        'D': np.random.randint(0, 100, n)
    })

    results = {}

    # === 技巧1：.values 或 .to_numpy() 替代逐行遍历 ===

    # 慢：iterrows
    start = time.perf_counter()
    total = 0
    for idx, row in df[['A', 'B']].iterrows():
        total += row['A'] * row['B']
    results['iterrows()'] = time.perf_counter() - start

    # 快：直接向量运算
    start = time.perf_counter()
    total = (df['A'] * df['B']).sum()
    results['向量化'] = time.perf_counter() - start

    # 最快：转换为NumPy后再运算
    start = time.perf_counter()
    arr_A = df['A'].values  # 或 .to_numpy()
    arr_B = df['B'].values
    total = np.dot(arr_A, arr_B)
    results['NumPy dot'] = time.perf_counter() - start

    # === 技巧2：.apply() vs transform vs 向量化 ===

    # 慢：apply逐行
    start = time.perf_counter()
    result = df['A'].apply(lambda x: x ** 2 + x * 0.5 - 1)
    results['apply()'] = time.perf_counter() - start

    # 快：向量化
    start = time.perf_counter()
    result = df['A'] ** 2 + df['A'] * 0.5 - 1
    results['向量化运算'] = time.perf_counter() - start

    # === 技巧3：使用 категорические 数据类型 ===

    # 对比：字符串 vs category
    df_str = df.copy()
    df_cat = df.copy()
    df_cat['C'] = df_cat['C'].astype('category')

    # cat类型的groupby更快
    start = time.perf_counter()
    _ = df_str.groupby('C')['A'].mean()
    results['groupby(string)'] = time.perf_counter() - start

    start = time.perf_counter()
    _ = df_cat.groupby('C')['A'].mean()
    results['groupby(category)'] = time.perf_counter() - start

    # === 技巧4：inplace=True并不总是好选择 ===
    # inplace可能会创建中间副本（copy），实际上比赋值慢
    # 但在内存受限时，inplace可以减少峰值内存使用

    # === 技巧5：使用合适的dtypes ===
    # float64 -> float32 (减少50%内存，10-20%加速)
    df_opt = df.copy()
    df_opt['A'] = df_opt['A'].astype('float32')
    df_opt['B'] = df_opt['B'].astype('float32')
    df_opt['D'] = df_opt['D'].astype('int16')  # 0-99，int16足够

    print("=" * 50)
    print("Pandas性能优化技巧对比")
    print("=" * 50)
    print(f"数据量: {n:,} 行")
    for method, elapsed in sorted(results.items(), key=lambda x: x[1]):
        print(f"  {method:<25} {elapsed:>8.4f} 秒")

    print(f"\n内存使用: 默认={df.memory_usage(deep=True).sum()/1e6:.1f}MB, "
          f"优化后={df_opt.memory_usage(deep=True).sum()/1e6:.1f}MB")

    return results
