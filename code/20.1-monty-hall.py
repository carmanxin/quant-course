# @quantlab/output: 20.1-monty-hall
import numpy as np
np.random.seed(42)
n_trials = 10000
stay_wins = 0
switch_wins = 0
for _ in range(n_trials):
    doors = [0, 0, 0]
    car = np.random.randint(0, 3)
    doors[car] = 1
    choice = np.random.randint(0, 3)
    goat_doors = [i for i in range(3) if i != choice and doors[i] == 0]
    opened = np.random.choice(goat_doors)
    switched_choice = [i for i in range(3) if i != choice and i != opened][0]
    if doors[choice] == 1:
        stay_wins += 1
    if doors[switched_choice] == 1:
        switch_wins += 1
print(f'Monty Hall 问题模拟 (n={n_trials:,})')
print(f'坚持原选择胜率: {stay_wins/n_trials:.1%}')
print(f'换门胜率: {switch_wins/n_trials:.1%}')
print(f'\n结论: 换门的获胜概率是坚持的 {switch_wins/stay_wins:.1f} 倍')
