# @quantlab/output: ffd9c2dc
import pandas as pd

def trading_book_stress_test(positions: dict,
                              risk_factors: dict,
                              stress_shocks: pd.DataFrame,
                              pricing_functions: dict = None) -> dict:
    """
    交易账户的系统性压力测试。

    参数:
        positions: {头寸ID: {risk_factors: sensitivity}}
            sensitivity是头寸对各风险因子的敏感性（PV01, delta, vega等）
        risk_factors: {因子名: 当前值}
        stress_shocks: (N_scenarios, M_factors) 各风险因子在各情景下的冲击
        pricing_functions: {头寸类型: 定价函数} 可选，用于非线性头寸
    返回:
        各情景下的P&L
    """
    results = []

    for scenario_name, shocks in stress_shocks.iterrows():
        scenario_pnl = 0
        position_pnls = {}

        for position_id, sensitivities in positions.items():
            position_pnl = 0

            for factor, sensitivity in sensitivities.items():
                if factor in shocks:
                    shock = shocks[factor]

                    # 线性近似
                    linear_pnl = sensitivity * shock * risk_factors.get(
                        factor, 1.0
                    )

                    # 如果有定价函数，加入非线性项（gamma等）
                    if pricing_functions and position_id in pricing_functions:
                        nonlinear_pnl = pricing_functions[position_id](
                            risk_factors, shocks
                        )
                        position_pnl += nonlinear_pnl
                    else:
                        position_pnl += linear_pnl

            scenario_pnl += position_pnl
            position_pnls[position_id] = position_pnl

        results.append({
            'Scenario': scenario_name,
            'Total_PnL': scenario_pnl,
            'Position_PnLs': position_pnls
        })

    return results

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
positions = {'债券A': {'rates': -40000}, '股票B': {'equity': 300000}}
risk_factors = {'rates': 0.03, 'equity': 4000}
stress_shocks = pd.DataFrame({
    'rates': [0.01, 0.02, -0.005],
    'equity': [-0.15, -0.30, 0.05],
}, index=['加息+股跌', '滞胀', '温和复苏'])
_tb = trading_book_stress_test(positions, risk_factors, stress_shocks)
for _row in _tb:
    print(_row)
