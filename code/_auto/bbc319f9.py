# @quantlab/output: bbc319f9
# 蝶式套利检测
def check_butterfly_arbitrage(strikes, ivs, T, r, S0):
    """
    检测波动率曲面上的蝶式套利
    strikes: 行权价序列（已排序）
    ivs: 对应的隐含波动率序列
    """
    n = len(strikes)
    arbitrage_flags = []

    for i in range(1, n-1):
        K1, K2, K3 = strikes[i-1], strikes[i], strikes[i+1]
        # 构建蝶式：买入K1和K3的一份，卖出K2的两份
        w = (K3 - K1) / (K3 - K2)  # 权重
        # 简化价格比较（实际需用BS公式计算精确价格）
        butterfly_cost = ivs[i-1] + (1-w)*ivs[i+1] - (1+(1-w))*ivs[i]
        if butterfly_cost < -0.001:  # 容忍度
            arbitrage_flags.append((K1, K2, K3, butterfly_cost))

    return arbitrage_flags
