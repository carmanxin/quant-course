# @quantlab/output: ef42bdaf
import numpy as np

def decompose_credit_spread(corp_yield, risk_free_rate, recovery_rate,
                             liquidity_premium=0, tax_adj=0):
    """
    信用利差的分解
    corp_yield: 公司债收益率
    risk_free_rate: 同期限无风险利率
    recovery_rate: 预期回收率（1 - LGD）
    liquidity_premium: 流动性溢价估计（bp）
    tax_adj: 税收调整（bp）
    """
    spread = (corp_yield - risk_free_rate) * 10000  # 转为基点

    # 假设风险中性违约概率可以从 CDS 市场或其他来源获得
    # 这里用简化方式分解
    expected_loss_component = spread - liquidity_premium - tax_adj

    # 隐含违约概率（简化：λ ≈ spread / (1 - recovery_rate)）
    implied_hazard_rate = (expected_loss_component / 10000) / (1 - recovery_rate)

    return {
        'total_spread_bps': spread,
        'liquidity_bps': liquidity_premium,
        'tax_bps': tax_adj,
        'expected_loss_bps': expected_loss_component,
        'implied_hazard_rate': implied_hazard_rate
    }

# 示例
result = decompose_credit_spread(
    corp_yield=0.055, risk_free_rate=0.035,
    recovery_rate=0.40, liquidity_premium=20, tax_adj=5
)
for k, v in result.items():
    print(f"  {k}: {v:.2f}")
