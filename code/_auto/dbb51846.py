# @quantlab/output: dbb51846
# rebalancing_schedule 伪代码结构
# 1. 计算负债最大期限 horizon
# 2. 按 rebalance_freq 步进到 horizon
# 3. 在每个再平衡点过滤剩余负债
# 4. 计算久期缺口并调整组合匹配
