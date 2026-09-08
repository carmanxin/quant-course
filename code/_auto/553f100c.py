# @quantlab/output: 553f100c
import numpy as np


def simulate_disease_test(n_population: int = 100000,
                           prevalence: float = 0.01,
                           sensitivity: float = 0.99,
                           specificity: float = 0.99) -> dict:
    """蒙特卡洛模拟疾病检测问题"""

    # 生成人群
    n_sick = int(n_population * prevalence)
    n_healthy = n_population - n_sick

    # 检测结果
    # 患病者检测阳性概率 = sensitivity
    sick_positive = np.random.binomial(1, sensitivity, n_sick).sum()

    # 健康者检测阳性概率 = 1 - specificity
    healthy_positive = np.random.binomial(1, 1 - specificity, n_healthy).sum()

    total_positive = sick_positive + healthy_positive

    true_positive_rate = sick_positive / total_positive if total_positive > 0 else 0

    theoretical = (sensitivity * prevalence) / \
                  (sensitivity * prevalence + (1 - specificity) * (1 - prevalence))

    return {
        'simulated_rate': true_positive_rate,
        'theoretical_rate': theoretical,
        'n_sick': n_sick,
        'n_healthy': n_healthy,
        'sick_positive': sick_positive,
        'healthy_positive': healthy_positive,
        'total_positive': total_positive
    }


# 运行模拟
result = simulate_disease_test()
print(f"理论概率: {result['theoretical_rate']:.4f}")
print(f"模拟概率: {result['simulated_rate']:.4f}")
print(f"检测阳性总人数: {result['total_positive']}")
print(f"其中真患病者: {result['sick_positive']}")
print(f"其中假阳性: {result['healthy_positive']}")
