# @quantlab/output: 98333cf7
def scenario_analysis(portfolio_durations, scenario_shifts):
    """
    利率情景分析
    portfolio_durations: dict {maturity: modified_duration * position_value}
    scenario_shifts: dict {maturity: rate_change_bps}
    """
    total_pnl = 0
    for maturity, dv01 in portfolio_durations.items():
        # 线性近似：PnL = -DV01 * rate_change_bps / 10000 * notional
        shift = scenario_shifts.get(maturity, 0)
        pnl = -dv01 * shift
        total_pnl += pnl
        print(f"  期限 {maturity}y: DV01={dv01:.0f}, 变动 {shift:+d}bp -> PnL={pnl:+.0f}")

    return total_pnl
