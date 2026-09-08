# @quantlab/output: c45a8ece
industry_exposure = np.zeros(n_industries)
for i, w in enumerate(weights):
    industry_exposure[industry[i]] += w * market_cap[i]
# 优化中加入等式约束令industry_exposure = 0
