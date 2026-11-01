# @quantlab/output: cfe17923
def predict_funding_rate(price_momentum_24h, oi_change_24h, basis_bps,
                          sentiment_index, model_weights=None):
    """
    资金费率方向预测模型
    """
    if model_weights is None:
        model_weights = {
            'momentum': 0.30,
            'oi_change': 0.25,
            'basis': 0.20,
            'sentiment': 0.25
        }

    # 各因子标准化到 [-1, 1]
    momentum_z = np.clip(price_momentum_24h / 0.10, -3, 3) / 3  # 假设10%为极限
    oi_z = np.clip(oi_change_24h / 0.20, -3, 3) / 3
    basis_z = np.clip(basis_bps / 50, -3, 3) / 3
    sentiment_z = np.clip((sentiment_index - 50) / 30, -3, 3) / 3

    # 加权预测
    predicted_change = (
        model_weights['momentum'] * momentum_z
        + model_weights['oi_change'] * oi_z
        + model_weights['basis'] * basis_z
        + model_weights['sentiment'] * sentiment_z
    )

    return {
        'predicted_direction': 'higher' if predicted_change > 0.2 else 'lower' if predicted_change < -0.2 else 'stable',
        'confidence': abs(predicted_change),
        'factor_contributions': {
            'momentum': model_weights['momentum'] * momentum_z,
            'oi_change': model_weights['oi_change'] * oi_z,
            'basis': model_weights['basis'] * basis_z,
            'sentiment': model_weights['sentiment'] * sentiment_z
        }
    }
