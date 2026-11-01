# @quantlab/output: 13cb7bb8
def limit_down_reversal_signal(daily_data: pd.DataFrame,
                                consecutive_limit_downs: int = 2) -> pd.Series:
    """
    跌停板逆向策略信号

    逻辑：连续跌停后首次开板，可能是恐慌情绪的逆转点
    """
    daily = daily_data.copy()

    # 计算跌停价
    daily['limit_down'] = daily['pre_close'] * 0.90

    # 识别跌停日
    daily['is_limit_down'] = daily['close'] <= daily['limit_down'] + 0.001

    # 连续跌停计数
    daily['consecutive_ld'] = daily.groupby('code')['is_limit_down'].transform(
        lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumcount() + 1)
    )

    # 信号条件：
    # 1. 前一日连续跌停 >= consecutive_limit_downs
    # 2. 当日不再跌停（开板）
    # 3. 当日成交量放大（相对前5日均值的1.5倍）
    prev_consecutive = daily.groupby('code')['consecutive_ld'].shift(1)

    avg_vol_5d = daily.groupby('code')['volume'].transform(
        lambda x: x.rolling(5).mean()
    )

    signal = (prev_consecutive >= consecutive_limit_downs) & \
             (~daily['is_limit_down']) & \
             (daily['volume'] > avg_vol_5d * 1.5) & \
             (daily['close'] > daily['open'])  # 当日收阳

    return signal.astype(int)

# ===== 合成数据最小示例: 限跌反转（数据为模拟，机制真实）=====
np.random.seed(107)
_rows = []
_pre = 10.0
for _i in range(12):
    _d = f'2024-05-{_i+1:02d}'
    if _i in (6, 7, 8):
        _close = round(_pre * 0.90, 2)   # 连续三日跌停
        _is_ld = 1
    else:
        _close = round(_pre * 1.01, 2)
        _is_ld = 0
    _rows.append({'date': _d, 'code': '600001', 'open': round(_pre * 0.98, 2),
                  'close': _close, 'pre_close': _pre,
                  'limit_down': round(_pre * 0.90, 2),
                  'is_limit_down': _is_ld,
                  'consecutive_ld': 0, 'volume': abs(np.random.randn()) * 5e6 + 1e6})
    _pre = _close
daily_data = pd.DataFrame(_rows)
print(limit_down_reversal_signal(daily_data))
