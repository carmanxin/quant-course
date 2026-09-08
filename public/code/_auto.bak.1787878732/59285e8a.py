# @quantlab/output: 59285e8a
from __future__ import annotations

import numpy as np


def walk_forward_splits(n: int, train: int, test: int, gap: int = 0):
    """生成扩展窗口切分，gap 用来隔离标签重叠。"""
    test_start = train + gap
    while test_start + test <= n:
        train_idx = np.arange(0, test_start - gap)
        test_idx = np.arange(test_start, test_start + test)
        yield train_idx, test_idx
        test_start += test


for fold, (tr, te) in enumerate(walk_forward_splits(1_000, 500, 100, gap=5), 1):
    assert tr.max() < te.min() - 5
    print(f"fold={fold}, train={tr[0]}:{tr[-1]}, test={te[0]}:{te[-1]}")
