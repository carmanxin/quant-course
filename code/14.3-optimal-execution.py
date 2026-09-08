# @quantlab/output: 14.3-optimal-execution
import numpy as np
X, T, sigma, eta, gamma = 100000, 1.0, 0.02, 2.5e-7, 2.5e-6
kappa = np.sqrt(gamma * sigma**2 / eta)
dt = T / 100
t = np.linspace(0, T, 101)
x = X * np.sinh(kappa * (T - t)) / np.sinh(kappa * T)
v = -np.gradient(x, dt)
print(f'总头寸: {X:,.0f} 股, 执行时间: {T} 天')
print(f'市场波动: {sigma*100:.1f}%, 临时冲击: {eta:.2e}')
print(f'\n时间\t剩余\t执行速率')
for i in range(0, 101, 10):
    print(f'{t[i]:.2f}\t{x[i]:,.0f}\t{v[i]:,.0f}')
print(f'\n初始执行速率: {v[0]:,.0f} 股/天')
print(f'最终执行速率: {v[-1]:,.0f} 股/天')
