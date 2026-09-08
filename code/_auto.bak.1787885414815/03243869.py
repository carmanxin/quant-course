# @quantlab/output: 03243869
def macaulay_duration(cashflows, times, ytm):
    """
    计算 Macaulay 久期
    cashflows: 各期现金流（含本金和利息）
    times: 各期现金流的时间（年）
    ytm: 到期收益率
    """
    pv = []
    weighted_pv = []
    for cf, t in zip(cashflows, times):
        pv_cf = cf / (1 + ytm) ** t
        pv.append(pv_cf)
        weighted_pv.append(t * pv_cf)

    price = sum(pv)
    duration = sum(weighted_pv) / price
    return duration, price

# 示例：10年期债券，票面利率4%，YTM=4.5%
face_value = 100
coupon_rate = 0.04
ytm = 0.045
years = 10
freq = 2  # 半年付息
n = years * freq
coupon = face_value * coupon_rate / freq
cashflows = [coupon] * n
cashflows[-1] += face_value
times = [(i + 1) / freq for i in range(n)]

dur, price = macaulay_duration(cashflows, times, ytm)
print(f"Macaulay 久期: {dur:.2f} 年")
print(f"债券全价: {price:.2f}")
