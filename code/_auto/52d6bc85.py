# @quantlab/output: 52d6bc85
import random


def reservoir_sampling(stream, k: int) -> list:
    """
    蓄水池抽样算法
    从流式数据中均匀地随机抽取 k 个元素

    时间复杂度: O(n), 空间复杂度: O(k)
    """
    reservoir = []

    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            # 以 k/(i+1) 的概率替换
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item

    return reservoir


# 验证均匀性
def verify_reservoir_sampling(n_trials: int = 10000,
                                stream_size: int = 100,
                                k: int = 10) -> dict:
    """验证蓄水池抽样的均匀性"""
    counts = {i: 0 for i in range(stream_size)}

    for _ in range(n_trials):
        stream = range(stream_size)
        sampled = reservoir_sampling(stream, k)
        for item in sampled:
            counts[item] += 1

    expected = n_trials * k / stream_size
    chi_sq = sum((c - expected) ** 2 / expected for c in counts.values())

    return {'expected_count': expected, 'chi_squared': chi_sq, 'counts': counts}


random.seed(42)

# 1) 单次抽样看结果
sample = reservoir_sampling(range(1000), k=10)
print(f"从 0..999 的流中抽 10 个: {sorted(sample)}")

# 2) 均匀性验证
res = verify_reservoir_sampling(n_trials=10000, stream_size=100, k=10)
counts = res['counts']
expected = res['expected_count']
chi_sq = res['chi_squared']

print(f"\n均匀性验证 (10000 次试验, 流长 100, k=10):")
print(f"  每个元素的期望入选次数: {expected:.0f}")
print(f"  实际最少 / 最多:        {min(counts.values())} / {max(counts.values())}")
print(f"  卡方统计量:             {chi_sq:.2f}  (自由度 99)")

# 自由度 99 时 chi2 的 95% 临界值约 123.2；均匀分布下 chi_sq 应在 99 附近
verdict = "通过（无法拒绝均匀假设）" if chi_sq < 123.2 else "未通过（分布可疑）"
print(f"  95% 临界值 123.2 → {verdict}")

print("\n  头部/尾部元素入选次数抽查（应大致相同，无位置偏好）:")
for i in [0, 1, 2, 49, 50, 97, 98, 99]:
    bar = '#' * int(counts[i] / expected * 30)
    print(f"    元素 {i:>3}: {counts[i]:>5} 次  {bar}")
