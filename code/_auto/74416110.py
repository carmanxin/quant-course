# @quantlab/output: 74416110
import matplotlib.pyplot as plt

# 模拟不同到期时间下的 Gamma
S_range = np.linspace(80, 120, 200)
K = 100
sig = 0.20
r = 0.03

for T in [0.01, 0.05, 0.25, 0.50]:
    gammas = []
    for S in S_range:
        d1 = (np.log(S/K) + (r + sig**2/2)*T) / (sig*np.sqrt(T))
        gammas.append(norm.pdf(d1) / (S * sig * np.sqrt(T)))
    plt.plot(S_range, gammas, label=f'T={T:.2f}')

plt.axvline(x=K, color='gray', linestyle='--', alpha=0.5)
plt.xlabel('标的资产价格 S')
plt.ylabel('Gamma')
plt.legend()
plt.title('不同到期时间下的 Gamma 曲线')
