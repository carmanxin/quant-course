# @quantlab/output: eff8bb38
import pandas as pd
import numpy as np

def efficient_data_pipeline(raw_prices):
    """
    展示使用Pandas链式操作构建高效数据处理管道
    """

    # 方法1: 传统的逐步操作（可读性好但效率低）
    def traditional_approach(df):
        df = df.copy()
        df['return'] = df['Close'].pct_change()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA60'] = df['Close'].rolling(60).mean()
        df['signal'] = (df['MA20'] > df['MA60']).astype(int)
        df['signal'] = df['signal'].shift(1)
        df['strategy_return'] = df['signal'] * df['return']
        return df

    # 方法2: 链式操作（更优雅，Pandas推荐风格）
    def chained_approach(df):
        return (df
            .assign(
                return_=lambda d: d['Close'].pct_change(),
                MA20=lambda d: d['Close'].rolling(20).mean(),
                MA60=lambda d: d['Close'].rolling(60).mean()
            )
            .assign(
                signal=lambda d: (d['MA20'] > d['MA60']).astype(int).shift(1)
            )
            .assign(
                strategy_return=lambda d: d['signal'] * d['return_']
            )
            .dropna()
        )

    # 方法3: 使用Polars的惰性计算（LazyFrame）
    def polars_approach(filepath):
        import polars as pl

        return (pl.scan_csv(filepath)
            .with_columns([
                pl.col('Close').pct_change().alias('return_'),
                pl.col('Close').rolling_mean(20).alias('MA20'),
                pl.col('Close').rolling_mean(60).alias('MA60'),
            ])
            .with_columns([
                (pl.col('MA20') > pl.col('MA60')).cast(pl.Int64).shift(1).alias('signal')
            ])
            .with_columns([
                (pl.col('signal') * pl.col('return_')).alias('strategy_return')
            ])
            .collect()  # 在此刻执行所有惰性计算
        )

    return chained_approach(raw_prices)
