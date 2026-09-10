# @quantlab/output: 11e7af69
import pandas as pd
import numpy as np

def build_continuous_futures(contracts_data, roll_rule='volume', roll_days_before=5):
    """
    构建期货连续价格序列

    contracts_data: DataFrame, 包含字段:
        - date: 交易日
        - symbol: 合约代码 (如 'IF2401', 'IF2402')
        - close: 收盘价
        - volume: 成交量
        - open_interest: 持仓量
    roll_rule: 展期规则 'volume'(量最大)/'oi'(持仓最大)/'fixed'(到期前N日)
    roll_days_before: fixed规则下，到期前多少天切换
    """
    df = contracts_data.copy()
    df['date'] = pd.to_datetime(df['date'])

    # 提取品种和到期月份
    df['product'] = df['symbol'].str.extract(r'([A-Za-z]+)')
    df['month'] = df['symbol'].str.extract(r'(\d{4})$')
    df['year'] = df['month'].str[:2].astype(int) + 2000
    df['mon'] = df['month'].str[2:].astype(int)

    # 按日期排序
    df = df.sort_values(['product', 'date'])

    results = {}

    for product in df['product'].unique():
        prod_df = df[df['product'] == product].copy()

        # 找出每个交易日的主力合约
        if roll_rule == 'volume':
            prod_df['rank_vol'] = prod_df.groupby('date')['volume'].rank(ascending=False)
            dominant = prod_df[prod_df['rank_vol'] == 1].copy()
            next_dominant = prod_df[prod_df['rank_vol'] == 2].copy()
        elif roll_rule == 'oi':
            prod_df['rank_oi'] = prod_df.groupby('date')['open_interest'].rank(ascending=False)
            dominant = prod_df[prod_df['rank_oi'] == 1].copy()

        # 检测主力合约切换点
        dominant = dominant.set_index('date').sort_index()
        dominant['prev_symbol'] = dominant['symbol'].shift(1)
        dominant['roll_date'] = dominant['symbol'] != dominant['prev_symbol']

        # 展期日列表
        roll_dates = dominant.index[dominant['roll_date']].tolist()

        # 构建连续价格（价差拼接法）
        continuous = dominant[['close', 'volume', 'symbol']].copy()
        continuous['roll_adjustment'] = 0.0

        cumulative_adj = 0.0
        for roll_date in roll_dates[1:]:  # 跳过第一个（没有前值可比较）
            # 找到切换日前后的新旧主力合约价格
            mask_before = (continuous.index < roll_date) & (continuous.index >= roll_dates[roll_dates.index(roll_date)-1])
            mask_after = continuous.index >= roll_date

            if mask_before.any() and mask_after.any():
                prev_price = continuous.loc[mask_before, 'close'].iloc[-1]
                # 在roll_date那一天，新旧合约的价格差异
                if roll_date in prod_df['date'].values:
                    day_data = prod_df[prod_df['date'] == roll_date]
                    old_contract = continuous.loc[continuous.index < roll_date, 'symbol'].iloc[-1]
                    new_contract = continuous.loc[roll_date, 'symbol'] if roll_date in continuous.index else None

                    if old_contract is not None:
                        old_price = day_data[day_data['symbol'] == old_contract]['close'].values
                        if len(old_price) > 0 and new_contract is not None:
                            new_price_day = day_data[day_data['symbol'] == new_contract]['close'].values
                            if len(new_price_day) > 0:
                                cumulative_adj += (new_price_day[0] - old_price[0])

                continuous.loc[mask_before, 'roll_adjustment'] = -cumulative_adj

        # 调整后的连续价格
        continuous['adjusted_close'] = continuous['close'] + continuous['roll_adjustment']

        results[product] = continuous

    return results


def futures_term_structure(contracts_data, target_date=None):
    """
    分析期货的期限结构（升水/贴水）

    期限结构是多空商品策略的关键alpha来源
    """
    df = contracts_data.copy()
    df['date'] = pd.to_datetime(df['date'])

    if target_date is None:
        target_date = df['date'].max()

    # 提取某一天所有合约的价格
    day_data = df[df['date'] == target_date].copy()
    day_data['month'] = day_data['symbol'].str.extract(r'(\d{4})$')
    day_data['mon_num'] = day_data['month'].str[2:].astype(int)

    # 按到期月排序
    day_data = day_data.sort_values('mon_num')

    # 计算展期收益率 (Roll Yield)
    # 展期收益 = (近月价格 - 远月价格) / 近月价格
    # 正 = 贴水 (Backwardation, 做多有利)
    # 负 = 升水 (Contango, 做多不利)

    if len(day_data) >= 2:
        front_price = day_data['close'].iloc[0]
        second_price = day_data['close'].iloc[1]
        roll_yield = (front_price - second_price) / front_price
        structure = 'Backwardation (贴水)' if roll_yield > 0 else 'Contango (升水)'

        return {
            'date': target_date,
            'front_month': day_data['symbol'].iloc[0],
            'front_price': front_price,
            'second_month': day_data['symbol'].iloc[1],
            'second_price': second_price,
            'roll_yield': roll_yield,
            'structure': structure
        }

    return None
