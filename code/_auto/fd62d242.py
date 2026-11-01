# @quantlab/output: fd62d242
# VIX 期限结构分析
# VIX 期货价格反映市场对未来波动率的预期
vix_spot = 18.5
vix_futures = {
    '1M': 19.2,
    '2M': 19.8,
    '3M': 20.1,
    '6M': 20.5,
    '9M': 20.3,
}
# 计算期限结构斜率
months = [1, 2, 3, 6, 9]
futures_vals = [19.2, 19.8, 20.1, 20.5, 20.3]

# contango 程度：远期 vs 即期
contango = futures_vals[-1] - vix_spot
print(f"期限结构为: {'Contango' if contango > 0 else 'Backwardation'}")
print(f"Contango/Backwardation 程度: {contango:.1f} 个波动率点")
