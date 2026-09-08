# @quantlab/output: b1f7c343
import heapq


class MedianFinder:
    """数据流中位数维护器"""

    def __init__(self):
        self.max_heap = []  # 存储较小的一半（取负实现大根堆）
        self.min_heap = []  # 存储较大的一半（小根堆）

    def add(self, num: float):
        """添加一个数值"""
        if not self.max_heap or num <= -self.max_heap[0]:
            heapq.heappush(self.max_heap, -num)
        else:
            heapq.heappush(self.min_heap, num)

        # 平衡两个堆（大小差不超过1）
        if len(self.max_heap) > len(self.min_heap) + 1:
            heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))
        elif len(self.min_heap) > len(self.max_heap):
            heapq.heappush(self.max_heap, -heapq.heappop(self.min_heap))

    def median(self) -> float:
        """查询当前中位数"""
        if len(self.max_heap) > len(self.min_heap):
            return -self.max_heap[0]
        else:
            return (-self.max_heap[0] + self.min_heap[0]) / 2.0
