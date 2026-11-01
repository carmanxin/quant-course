# @quantlab/output: 0d661a4c
def convexity(cashflows, times, ytm):
    """
    计算债券的凸度
    """
    pv_cf = [cf / (1 + ytm) ** t for cf, t in zip(cashflows, times)]
    weighted_pv = [t * (t + 1) * pv for t, pv in zip(times, pv_cf)]
    price = sum(pv_cf)
    conv = sum(weighted_pv) / (price * (1 + ytm)**2)
    return conv

# 凸度对价格估计的改进
conv = convexity(cashflows, times, ytm)
print(f"凸度: {conv:.2f}")

# 假设收益率上升50bp
dy = 0.0050
mod_dur = dur / (1 + ytm / freq)
pct_change_linear = -mod_dur * dy
pct_change_convexity = pct_change_linear + 0.5 * conv * dy**2
print(f"一阶近似: {pct_change_linear*100:.4f}%")
print(f"二阶近似: {pct_change_convexity*100:.4f}%")
print(f"凸度调整: {0.5 * conv * dy**2 * 100:.4f}%")
