# @quantlab/output: b87c5fe1
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

def calculate_bei(nominal_yields: pd.DataFrame,
                   tips_yields: pd.DataFrame) -> pd.DataFrame:
    """
    计算各期限的盈亏平衡通胀率。

    参数:
        nominal_yields: 名义国债收益率，列为各期限
        tips_yields: TIPS收益率，列为各期限
    返回:
        BEI DataFrame
    """
    # 对齐期限
    common_tenors = nominal_yields.columns.intersection(tips_yields.columns)
    bei = nominal_yields[common_tenors] - tips_yields[common_tenors]
    bei.columns = [f'BEI_{c}' for c in common_tenors]

    return bei


def bei_term_structure(bei_latest: pd.Series) -> dict:
    """
    分析BEI的期限结构及其隐含信息。

    参数:
        bei_latest: 最新的BEI曲线（不同期限的BEI值）
    """
    tenors = np.array([float(str(c).replace('BEI_', '').replace('Y', ''))
                       for c in bei_latest.index])
    bei_values = bei_latest.values

    # 拟合曲线
    f = interp1d(tenors, bei_values, kind='cubic', fill_value='extrapolate')

    # 计算关键指标
    bei_5y = f(5)
    bei_10y = f(10)
    bei_30y = f(30)

    # 5年5年远期BEI
    bei_5y5y = ((1 + bei_10y / 100) ** 10 /
                (1 + bei_5y / 100) ** 5) ** (1/5) - 1
    bei_5y5y *= 100  # 转百分比

    # 通胀风险溢价（简化估计：长端BEI - 短期调查通胀预期）
    survey_lt_inflation = 2.0  # 简化：假设长期通胀预期调查为2%
    irp_estimate = bei_5y5y - survey_lt_inflation

    # 可视化
    fig, ax = plt.subplots(figsize=(10, 6))
    tenors_dense = np.linspace(1, 30, 100)
    bei_dense = f(tenors_dense)

    ax.plot(tenors_dense, bei_dense, 'b-', linewidth=2, label='BEI 拟合曲线')
    ax.scatter(tenors, bei_values, color='red', s=80, zorder=5,
               label='市场数据')
    ax.axhline(y=2.0, color='green', linestyle='--',
               label='美联储通胀目标 (2%)')
    ax.fill_between(tenors_dense, bei_dense, 2.0,
                     where=(bei_dense > 2.0),
                     alpha=0.2, color='red', label='通胀预期高于目标')
    ax.set_xlabel('期限（年）')
    ax.set_ylabel('BEI (%)')
    ax.set_title('盈亏平衡通胀率期限结构')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.show()

    return {
        'BEI_5Y': bei_5y,
        'BEI_10Y': bei_10y,
        'BEI_30Y': bei_30y,
        'BEI_5Y5Y_forward': bei_5y5y,
        'IRP_estimate': irp_estimate,
        'term_premium_signal': 'steepening' if bei_30y > bei_5y else 'flattening'
    }
