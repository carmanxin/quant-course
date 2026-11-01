# @quantlab/output: 6a6c8a1a
# Vega 暴露对不同 IV 环境的敏感性分析
def vega_change(vega_pos, current_iv, target_iv):
    """IV 变化 X 个百分点带来的损益估算"""
    return vega_pos * (target_iv - current_iv) * 100

# 示例: 持有 Short Strangle, vega_pos = -0.5 (每张)
# 当前 IV = 25%, 预期 IV = 20%
print(f"IV 25% → 20%: {vega_change(-0.5, 0.25, 0.20)*10000:.0f} 元/张(每张 delta 10000 份)")
# 输出: 2500 (即做空 IV 5% 赚到 2500/张, 但还要扣 Theta 后的净损益等)
