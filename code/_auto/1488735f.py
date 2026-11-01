# @quantlab/output: 1488735f
# 陷阱
0.1 + 0.2 == 0.3  # False!

# 解决方案
import math
math.isclose(0.1 + 0.2, 0.3)  # True

# 或在金融计算中使用 Decimal
from decimal import Decimal
Decimal('0.1') + Decimal('0.2') == Decimal('0.3')  # True
