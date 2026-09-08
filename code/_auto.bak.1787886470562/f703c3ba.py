# @quantlab/output: f703c3ba
def bridge_crossing_optimizer(times: list) -> tuple:
    """
    四人过桥问题的最优方案

    Parameters
    ----------
    times : list
        四个人过桥所需时间，已经排序
    """
    times = sorted(times)
    a, b, c, d = times  # a最快, d最慢

    # 策略1：最快的两人轮流做摆渡人
    # a+b过, a回, c+d过, b回, a+b过
    strategy1 = b + a + d + b + b

    # 策略2：最快的一个人往返
    # a+d过, a回, a+c过, a回, a+b过
    strategy2 = d + a + c + a + b

    # 策略3：分两组（b+c过河也是一种方案）
    strategy3 = b + a + c + a + d

    best = min(strategy1, strategy2, strategy3)

    return best, {
        'strategy1': strategy1,
        'strategy2': strategy2,
        'strategy3': strategy3
    }


print(f"最优过桥时间: {bridge_crossing_optimizer([1, 2, 5, 10])[0]} 分钟")
