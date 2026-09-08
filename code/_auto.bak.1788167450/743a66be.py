# @quantlab/output: 743a66be
def birthday_probability(n_people: int, days: int = 365) -> float:
    """计算n人中至少两人同生日的概率"""
    prob_all_different = 1.0
    for i in range(n_people):
        prob_all_different *= (days - i) / days
    return 1 - prob_all_different


def find_birthday_threshold(target_prob: float = 0.5, days: int = 365) -> int:
    """找到达到目标概率所需的最小人数"""
    prob = 0
    n = 1
    while prob < target_prob:
        n += 1
        prob = birthday_probability(n, days)
    return n


print(f"23人生日概率: {birthday_probability(23):.3f}")
print(f"50%概率需要人数: {find_birthday_threshold(0.5)}")
