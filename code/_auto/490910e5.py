# @quantlab/output: 490910e5
import pandas as pd
import numpy as np


def efficient_return_calculation(prices: pd.DataFrame,
                                   periods: list = [1, 5, 20]) -> pd.DataFrame:
    """
    快速计算多个周期的收益率并处理异常值

    Parameters
    ----------
    prices : pd.DataFrame
        index=date, columns=stock_codes, values=close_price
    periods : list
        需要计算的收益周期列表
    """
    result = pd.DataFrame(index=prices.index)

    for p in periods:
        # 使用 pct_change 的 fill_method=None 避免前视偏差
        ret = prices.pct_change(p, fill_method=None)

        # 异常值处理：Winsorize
        for col in ret.columns:
            lower = ret[col].quantile(0.01)
            upper = ret[col].quantile(0.99)
            ret[col] = ret[col].clip(lower, upper)

        result[f'ret_{p}d'] = ret.stack()

    return result
