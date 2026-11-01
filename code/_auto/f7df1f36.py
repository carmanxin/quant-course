# @quantlab/output: f7df1f36
def multi_layer_protection(positions, market_data):
    """
    永续合约多层防护监控
    """
    alerts = []

    for pos in positions:
        rm = LiquidationRiskManager(
            pos['value'], pos['entry_price'],
            pos['leverage'], pos.get('maintenance_margin', 0.005)
        )

        liq_price = rm.liquidation_price(pos['is_long'])
        current_price = market_data[pos['symbol']]['price']
        distance_to_liq = abs(current_price - liq_price) / current_price

        # 第1层：预警线（距强平价10%）
        if distance_to_liq < 0.10:
            alerts.append({
                'level': 'WARNING',
                'symbol': pos['symbol'],
                'message': f"距强平价仅 {distance_to_liq*100:.1f}%",
                'action': '考虑减仓或追加保证金'
            })

        # 第2层：危险线（距强平价5%）
        if distance_to_liq < 0.05:
            alerts.append({
                'level': 'DANGER',
                'symbol': pos['symbol'],
                'message': f"距强平价仅 {distance_to_liq*100:.1f}%",
                'action': '立即减仓50%以上'
            })

        # 第3层：极端波动止损
        volatility_24h = market_data[pos['symbol']].get('volatility_24h', 0)
        if volatility_24h > 0.15:  # 日波动超过15%
            alerts.append({
                'level': 'EXTREME_VOL',
                'symbol': pos['symbol'],
                'message': f"24h波动率 {volatility_24h*100:.1f}%",
                'action': '检查所有持仓，收紧止损'
            })

    return sorted(alerts, key=lambda x: {'WARNING': 0, 'DANGER': 1, 'EXTREME_VOL': 2}[x['level']], reverse=True)
