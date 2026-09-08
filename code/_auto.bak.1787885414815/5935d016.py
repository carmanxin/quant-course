# @quantlab/output: 5935d016
import pandas as pd
import numpy as np

def calculate_adjustment_factor(dividends, splits, bonuses, rights, prices):
    """
    手动计算复权因子序列

    dividends: 每股现金分红
    splits: 拆股比例（如1拆2，splits=2）
    bonuses: 送股比例（如10送3，bonuses=0.3）
    rights: 配股比例和配股价
    prices: 调整前的收盘价（不复权价格）
    """

    # 合并所有事件按照发生日期
    events = []

    for date, div in dividends.items():
        events.append(('dividend', date, div))

    for date, split in splits.items():
        events.append(('split', date, split))

    for date, bonus in bonuses.items():
        events.append(('bonus', date, bonus))

    events.sort(key=lambda x: x[1])  # 按日期排序

    # 从最早的事件到最新，累积计算复权因子
    adj_factor = 1.0

    # 前复权因子（调整历史价格）
    # adj_factor_product[t] = 从第t天到最新日之间的所有调整因子的乘积
    adj_factors = pd.Series(1.0, index=prices.index)

    for event_type, date, value in events:
        if event_type == 'dividend':
            # 分红调整：找到除息日前后的价格
            if date in prices.index:
                cum_price = prices.loc[date]  # 除息前的价格（含权）
                # 调整因子 = (除权前价格 - 每股分红) / 除权前价格
                # 即价格需要乘以这个因子
                factor = (cum_price - value) / cum_price
                adj_factor *= factor

        elif event_type == 'bonus':
            # 送股：总市值不变，股数变多，每股价格变低
            # 10送3 => 10股变13股，价格变 10/13
            factor = 1 / (1 + value)
            adj_factor *= factor

        elif event_type == 'split':
            # 拆股：1拆2 => 1股变2股，价格变1/2
            factor = 1 / value
            adj_factor *= factor

    # 将累积调整因子应用到历史价格上
    # 因为是前向累积（从前往后），我们需要反向传播

    return adj_factors


def detect_corporate_actions(price_df, threshold=0.15):
    """
    从价格序列中检测可能的公司事件（分红/拆股等导致的跳跃）

    用于验证复权数据是否完整
    """
    df = price_df.copy()
    df['return'] = df['close'].pct_change()

    # 检测价格跳跃
    # 在有涨跌停限制的A股市场，单日收益率超过一定范围通常意味着公司事件
    jumps = df[df['return'].abs() > threshold]

    events = []
    for date, row in jumps.iterrows():
        # 检查是否伴随成交量异常
        prev_date = df.index[df.index.get_loc(date) - 1]
        vol_ratio = row.get('volume', 1) / df.loc[prev_date, 'volume']

        events.append({
            'date': date,
            'return': row['return'],
            'volume_ratio': vol_ratio,
            'likely_action': 'dividend/bonus/split' if vol_ratio > 2 else 'possible data error'
        })

    if events:
        print(f"检测到 {len(events)} 个可能的事件日:")
        for e in events[:10]:
            print(f"  {e['date'].date()}: 收益={e['return']:.2%}, "
                  f"量比={e['volume_ratio']:.1f}, 可能={e['likely_action']}")

    return events
