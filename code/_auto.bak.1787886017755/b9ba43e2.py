# @quantlab/output: b9ba43e2
import numpy as np
import matplotlib.pyplot as plt

# 模拟典型的波动率偏斜（指数期权）
strikes = np.linspace(80, 120, 50)
S0 = 100
# 偏斜模型：IV与moneyness呈负相关
atm_vol = 0.20
skew = -0.15  # 偏斜系数，负值表示左尾更高
iv = atm_vol + skew * (strikes - S0) / S0

plt.plot(strikes, iv * 100, 'b-', linewidth=2)
plt.axvline(x=S0, color='gray', linestyle='--')
plt.xlabel('行权价 K')
plt.ylabel('隐含波动率 (%)')
plt.title('波动率偏斜 (Volatility Skew)')
