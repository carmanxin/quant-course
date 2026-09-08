# @quantlab/output: e63df021
def vol_cone(prices, windows=[10,20,30,60,90,120,250]):
    """计算不同窗口 HV,并统计分位数"""
    log_returns = np.log(prices[1:] / prices[:-1])
    df = pd.DataFrame()
    for w in windows:
        df[f"HV_{w}"] = log_returns.rolling(w).std() * np.sqrt(252)

    # 各列分位数
    quantiles = df.describe(percentiles=[0.05,0.25,0.50,0.75,0.95]).T
    return df, quantiles

# 示例输出
df, q = vol_cone(prices)
print("波动率锥统计(年化):")
print(q[["mean","5%","25%","50%","75%","95%"]].applymap(lambda x: f"{x*100:.1f}%"))
