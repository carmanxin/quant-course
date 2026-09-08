# @quantlab/output: 571567bd
# 重要: 不同市场的隐含波动率偏度对比
# 美国 SPX: 25-delta 偏度通常 -5 到 -10
# 韩国 KO200: 偏度极负,因为散户强烈看空
# A 股 50ETF: 25-delta 偏度 -3 到 -8

# 隐含波动率偏度的构造方法 (Risk Reversal +1/-1 delta)
# 25-delta put IV - 25-delta call IV  = 偏度
# 这是衡量"暴跌恐惧"的市场指标
