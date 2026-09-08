# @quantlab/output: a25d6a24
import numpy as np
import pandas as pd
from typing import Tuple

def classify_trades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Lee-Ready 算法分类每笔交易的买卖方向。

    参数:
        df: 包含 price, bid, ask 列的 DataFrame
    返回:
        添加 trade_direction 列的 DataFrame (1=买方主动, -1=卖方主动)
    """
    df = df.copy()
    mid_price = (df['bid'] + df['ask']) / 2

    conditions = [
        df['price'] > mid_price,
        df['price'] < mid_price,
        df['price'] == mid_price
    ]
    choices = [1, -1, 0]

    df['trade_direction'] = np.select(conditions, choices, default=0)

    # Tick test: 相等时比较前一成交价
    df['price_change'] = df['price'].diff()
    df.loc[df['trade_direction'] == 0, 'trade_direction'] = np.where(
        df.loc[df['trade_direction'] == 0, 'price_change'] > 0, 1, -1
    )

    return df
