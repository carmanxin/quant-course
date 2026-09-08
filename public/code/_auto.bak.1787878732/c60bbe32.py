# @quantlab/output: c60bbe32
def vix_calc(otm_options_near, otm_options_far, T1, T2, F, r):
    """
    otm_options: list of tuples (K, mid_price)
    T1, T2: 近月、远月到期时间(年)
    F: 前向指数水平
    """
    K0 = min([k for k,_ in otm_options_near if k > F])
    K1_min = min([k for k,_ in otm_options_near])
    K2_max = max([k for k,_ in otm_options_near])

    def contrib(otm_options, T):
        sigma2 = 0
        n = len(otm_options)
        for i, (K, Q) in enumerate(otm_options):
            # 计算 Delta K (中心差分)
            K_minus = otm_options[i-1][0] if i > 0 else K1_min
            K_plus  = otm_options[i+1][0] if i < n-1 else K2_max
            dK = (K_plus - K_minus) / 2
            sigma2 += dK * Q / K**2
        return (2/T) * np.exp(r*T) * sigma2 - (1/T) * (F/K0 - 1)**2

    sigma2_1 = contrib(otm_options_near, T1)
    sigma2_2 = contrib(otm_options_far,  T2)
    # 加权到 30 天
    N1, N2 = int(T1*365), int(T2*365)
    N30 = 30
    VIX2 = sigma2_1 * (N2-N30)/(N2-N1) + sigma2_2 * (N30-N1)/(N2-N1)
    return np.sqrt(VIX2) * 100

# 示例
otm_near = [(95,0.20),(96,0.50),(97,1.00),(98,1.80),(99,2.80),
            (100,4.20),(101,5.50),(102,7.00),(103,8.50),(105,11.50)]
# 注: 实际应该只保留 OTM 的部分, 即 Put 用 K<F, Call 用 K>F
otm_near_clean = [(95,0.20),(96,0.50),(97,1.00),(98,1.80),(99,2.80),
                  (101,5.50),(102,7.00),(103,8.50),(105,11.50)]
otm_far  = [(93,0.40),(95,0.80),(97,1.50),(99,2.50),(100,3.60),
            (101,4.90),(103,7.20),(105,9.50),(107,12.00)]

vix_now = vix_calc(otm_near_clean, otm_far, 1/12, 2/12, F=99.5, r=0.05)
print(f"VIX 构造结果: {vix_now:.2f}")
print(f"分位数(<15:极低 / 15-20:正常 / 20-30:略高 / >30:恐慌): {'恐慌' if vix_now>30 else '略高' if vix_now>20 else '正常' if vix_now>15 else '极低'}")
