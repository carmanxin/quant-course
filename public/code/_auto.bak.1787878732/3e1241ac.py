# @quantlab/output: 3e1241ac
def simulate_monty_hall(n_trials: int = 100000) -> dict:
    """蒙特卡洛模拟三门问题"""
    stay_wins = 0
    switch_wins = 0

    for _ in range(n_trials):
        doors = [0, 0, 0]
        car = np.random.randint(0, 3)
        doors[car] = 1  # 1 表示汽车

        # 参赛者初始选择
        choice = np.random.randint(0, 3)

        # 主持人打开一扇有山羊的门（不是参赛者的选择，也不是汽车）
        available = [i for i in range(3) if i != choice and doors[i] == 0]
        opened = np.random.choice(available)

        # 换门选择
        other = [i for i in range(3) if i != choice and i != opened][0]

        if doors[choice] == 1:
            stay_wins += 1
        if doors[other] == 1:
            switch_wins += 1

    return {
        'stay_win_rate': stay_wins / n_trials,
        'switch_win_rate': switch_wins / n_trials
    }
