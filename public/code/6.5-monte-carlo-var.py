import numpy as np
np.random.seed(42)
initial = 100000
mu, sigma = 0.08, 0.20
days, confidence = 30, 0.95
n_sims = 5000
drift = (mu - 0.5 * sigma**2) / 252
vol = sigma / np.sqrt(252)
finals = []
sample_path = [initial]
sp = initial
for s in range(n_sims):
    p = initial
    for _ in range(days):
        p *= np.exp(drift + vol * np.random.randn())
    finals.append(p)
    if s == 0:
        sp = initial
        for _ in range(days):
            sp *= np.exp(drift + vol * np.random.randn())
            sample_path.append(sp)
finals.sort()
var_val = initial - finals[int((1 - confidence) * n_sims)]
tail = finals[:int((1 - confidence) * n_sims)]
cvar = initial - np.mean(tail)
print(f'{confidence*100:.0f}%置信度, {days}天VaR: ${var_val:,.2f}')
print(f'CVaR (尾部期望损失): ${cvar:,.2f}')
print(f'占初始资金: {var_val/initial*100:.2f}%')
