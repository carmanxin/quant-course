# @quantlab/output: f95806c7
def economic_cycle_scoreboard(indicators: dict) -> dict:
    """
    综合多指标打分当前经济周期位置。

    参数:
        indicators: 各指标的当前得分字典
            {'pmi': 55, 'unemployment': 3.5, 'retail_sales': 3.2, ...}
    返回:
        综合打分和周期判断
    """
    # 各指标的标准化规则
    scoring_rules = {
        'pmi': {
            'score': lambda x: min(100, max(0, (x - 45) / 15 * 100)),
            'weight': 0.20,
            'direction': 1  # PMI越高越好
        },
        'unemployment_rate': {
            'score': lambda x: min(100, max(0, (8 - x) / 5 * 100)),
            'weight': 0.15,
            'direction': -1  # 失业率越低越好
        },
        'retail_sales_yoy': {
            'score': lambda x: min(100, max(0, (x + 5) / 10 * 100)),
            'weight': 0.15,
            'direction': 1
        },
        'industrial_production_yoy': {
            'score': lambda x: min(100, max(0, (x + 5) / 10 * 100)),
            'weight': 0.15,
            'direction': 1
        },
        'credit_spread': {
            'score': lambda x: min(100, max(0, (5 - x) / 5 * 100)),
            'weight': 0.15,
            'direction': -1  # 信用利差越低越好
        },
        'yield_curve_slope': {
            'score': lambda x: min(100, max(0, (x + 1) / 3 * 100)),
            'weight': 0.10,
            'direction': 1  # 收益率曲线越陡越好
        },
        'housing_starts_yoy': {
            'score': lambda x: min(100, max(0, (x + 10) / 20 * 100)),
            'weight': 0.10,
            'direction': 1
        }
    }

    total_score = 0
    component_scores = {}

    for name, rules in scoring_rules.items():
        if name in indicators:
            raw_score = rules['score'](indicators[name])
            weighted = raw_score * rules['weight']
            total_score += weighted
            component_scores[name] = {
                'raw_value': indicators[name],
                'score': raw_score,
                'weighted_score': weighted
            }

    # 周期阶段判断
    if total_score > 65:
        phase = 'expansion'
    elif total_score > 45:
        phase = 'slow_growth'
    elif total_score > 25:
        phase = 'contraction_risk'
    else:
        phase = 'recession'

    return {
        'composite_score': total_score,
        'phase': phase,
        'component_scores': component_scores,
        'confidence': abs(total_score - 50) / 50  # 0到1
    }
