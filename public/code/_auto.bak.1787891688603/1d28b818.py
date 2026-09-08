# @quantlab/output: 1d28b818
from itertools import combinations


def generate_weighing_plan(n_balls: int, n_weighings: int) -> list:
    """
    生成n次天平称量的信息最大化的称量方案

    思路：每次称量将剩余候选尽可能三等分
    """
    # 状态空间：每个球可以是正常(0)、偏重(+1)、偏轻(-1)
    # 这是一个简化框架，完整的实现涉及搜索和剪枝

    plan = []
    remaining = list(range(n_balls))

    for round_idx in range(n_weighings):
        n = len(remaining)
        # 尽量三等分
        left_size = n // 3
        right_size = n // 3

        left = remaining[:left_size]
        right = remaining[left_size:left_size + right_size]
        unweighed = remaining[left_size + right_size:]

        plan.append({
            'round': round_idx + 1,
            'left': left,
            'right': right,
            'unweighed': unweighed
        })

    return plan
