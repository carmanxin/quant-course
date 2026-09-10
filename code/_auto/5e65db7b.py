# @quantlab/output: 5e65db7b
import heapq


class OnlineMedian:
    def __init__(self) -> None:
        self.low: list[float] = []
        self.high: list[float] = []

    def add(self, value: float) -> None:
        heapq.heappush(self.low, -value)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def value(self) -> float:
        if not self.low:
            raise ValueError("数据流为空")
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2.0


stream = OnlineMedian()
for x in [101, 99, 103, 100, 98]:
    stream.add(x)
    print(x, stream.value())
