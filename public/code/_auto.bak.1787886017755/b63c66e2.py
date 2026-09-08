# @quantlab/output: b63c66e2
# 两期 Greeks 矩阵求解对冲比例
# 目标：构建一个组合使得 Delta=0, Gamma=0
# 使用期权A和期权B来对冲
import numpy as np

# 期权A的Greeks
A = {'delta': 0.6, 'gamma': 0.03, 'vega': 0.15}
# 期权B的Greeks
B = {'delta': 0.3, 'gamma': 0.02, 'vega': 0.10}
# 持仓期权的Greeks
P = {'delta': 1.0, 'gamma': -0.05, 'vega': -0.25}

# 方程: w_A * [A_delta, A_gamma] + w_B * [B_delta, B_gamma] = -[P_delta, P_gamma]
G = np.array([[A['delta'], B['delta']],
              [A['gamma'], B['gamma']]])
b = np.array([-P['delta'], -P['gamma']])
w_A, w_B = np.linalg.solve(G, b)
print(f"对冲比例: 期权A = {w_A:.2f}份, 期权B = {w_B:.2f}份")
