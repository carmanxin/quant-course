# @quantlab/output: c7371ec7
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

    return {'expected_count': expected, 'chi_squared': chi_sq}
