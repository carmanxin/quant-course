# @quantlab/output: f1ca0322
def triple_ma_strategy(df, short=10, mid=30, long=60):
    """
    三均线策略：用三根均线的排列关系判断趋势强度

    趋势排列：short > mid > long（强多头）
    反趋势排列：short < mid < long（强空头）
    纠缠状态：三线交叉混乱（不交易，过滤震荡）
    """
    data = df.copy()
    data['MA_s'] = data['Close'].rolling(short).mean()
    data['MA_m'] = data['Close'].rolling(mid).mean()
    data['MA_l'] = data['Close'].rolling(long).mean()

    # 信号逻辑
    data['trend_up'] = (data['MA_s'] > data['MA_m']) & (data['MA_m'] > data['MA_l'])
    data['trend_down'] = (data['MA_s'] < data['MA_m']) & (data['MA_m'] < data['MA_l'])

    # 仅在趋势明确时持仓
    data['position'] = 0
    data.loc[data['trend_up'].shift(1), 'position'] = 1
    data.loc[data['trend_down'].shift(1), 'position'] = -1  # 允许做空

    # 计算收益和换手率
    data['returns'] = data['Close'].pct_change()
    data['strategy_returns'] = data['position'] * data['returns']

    # 统计持仓时间比例
    in_market = (data['position'].abs() > 0).mean()
    print(f"持仓时间比例: {in_market:.1%}")

    return data
