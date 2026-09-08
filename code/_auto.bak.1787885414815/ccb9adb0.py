# @quantlab/output: ccb9adb0
def vrp_signal(iv, hv_20d, lookahead="revert"):
    """波动率风险溢价信号"""
    vrp = iv - hv_20d
    if vrp > 0.04:      # >4个百分点
        return "SELL_VOL"
    elif vrp < -0.02:   # 负2个百分点
        return "BUY_VOL"
    else:
        return "NEUTRAL"

# 模拟:用 252 天历史数据回看信号分布
signals = []
for i in range(60, len(prices)):
    hv_20 = pd.Series(log_returns).iloc[i-20:i].std()*np.sqrt(252)
    # 假设 IV 是观测到的值 (用 1.2 倍 HV 模拟)
    iv = hv_20 * 1.10 + np.random.normal(0, 0.02)
    sig = vrp_signal(iv, hv_20)
    signals.append(sig)

from collections import Counter
print("信号分布:", Counter(signals))
