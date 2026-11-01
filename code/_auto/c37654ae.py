# @quantlab/output: c37654ae
def risk_contribution_report(weights, Sigma):
    """
    生成风险贡献报告：展示每个资产的风险来源

    Parameters:
        weights: 组合权重
        Sigma: 协方差矩阵
    """
    port_vol = np.sqrt(weights @ Sigma @ weights)
    mrc = Sigma @ weights  # 边际风险贡献
    rc = weights * mrc / port_vol  # 风险贡献（百分比）

    report = pd.DataFrame({
        '权重': weights,
        '波动率': np.sqrt(np.diag(Sigma)),
        '边际风险贡献': mrc,
        '风险贡献(%)': rc * 100,
    })

    # 按风险贡献排序
    report = report.sort_values('风险贡献(%)', ascending=False)
    report['累积风险贡献(%)'] = report['风险贡献(%)'].cumsum()

    return report

# 示例：对比等权和风险平价的风险集中度
def concentration_analysis(weights, Sigma):
    """计算风险集中度指标"""
    rc = risk_contribution_report(weights, Sigma)['风险贡献(%)'] / 100

    # 赫芬达尔-赫希曼指数(HHI): 风险贡献越集中, HHI越高
    hhi = np.sum(rc ** 2)

    # 有效风险分散度: 1/HHI
    effective_n = 1 / hhi if hhi > 0 else np.inf

    print(f"风险集中度(HHI): {hhi:.4f}")
    print(f"有效分散度: {effective_n:.1f} (相当于{effective_n:.0f}个等风险资产)")

    return hhi, effective_n
