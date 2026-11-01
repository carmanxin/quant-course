# @quantlab/output: 453ee8ee
import numpy as np

def frtb_sba_capital(delta_charges: dict,
                      vega_charges: dict,
                      curvature_charges: dict) -> dict:
    """
    FRTB 标准法（基于敏感度的方法）资本汇总。

    总资本 = Delta资本 + Vega资本 + 曲率风险资本

    参数:
        delta_charges: 各风险类别的 Delta 资本
        vega_charges: 各风险类别的 Vega 资本
        curvature_charges: 各风险类别的曲率风险资本
    返回:
        FRTB-SA 总资本要求
    """
    risk_classes = list(delta_charges.keys())
    rho_inter = 0.5  # 类间相关系数

    # 各类别内 Delta+Vega+Curvature 简单加总
    class_capital = {}
    for cls in risk_classes:
        class_capital[cls] = (
            delta_charges.get(cls, 0) +
            vega_charges.get(cls, 0) +
            curvature_charges.get(cls, 0)
        )

    # 跨类别聚合
    total_capital = np.sqrt(
        sum(v**2 for v in class_capital.values()) +
        sum(class_capital[c1] * class_capital[c2] * rho_inter
            for i, c1 in enumerate(class_capital)
            for c2 in list(class_capital.keys())[i+1:])
    )

    return {
        'Delta_Charges': delta_charges,
        'Vega_Charges': vega_charges,
        'Curvature_Charges': curvature_charges,
        'Total_Capital_Charge': total_capital,
        'RWA': total_capital * 12.5
    }

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_f = frtb_sba_capital(delta_charges={'rates': 2e6, 'equity': 3e6},
                      vega_charges={'rates': 5e5, 'equity': 8e5},
                      curvature_charges={'rates': 1e5, 'equity': 2e5})
for _k, _v in _f.items():
    print(f'{_k}: {_v}')
