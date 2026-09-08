# @quantlab/output: f965c918
from collections import OrderedDict


class ReferenceLRU:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity 必须为正")
        self.capacity = capacity
        self.data: OrderedDict[str, int] = OrderedDict()

    def get(self, key: str) -> int | None:
        if key not in self.data:
            return None
        self.data.move_to_end(key, last=False)
        return self.data[key]

    def put(self, key: str, value: int) -> None:
        if key in self.data:
            del self.data[key]
        self.data[key] = value
        self.data.move_to_end(key, last=False)
        if len(self.data) > self.capacity:
            self.data.popitem(last=True)

    def assert_invariants(self) -> None:
        assert len(self.data) <= self.capacity
        assert len(self.data) == len(set(self.data))


cache = ReferenceLRU(2)
cache.put("A", 1)
cache.put("B", 2)
assert cache.get("A") == 1
cache.put("C", 3)
assert cache.get("B") is None
cache.assert_invariants()
print(list(cache.data.items()))
