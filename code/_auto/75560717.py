# @quantlab/output: 75560717
import pandas as pd
import numpy as np
import akshare as ak

def fetch_and_clean_a_stock(symbol, start_date, end_date, adjust='qfq'):
    """
    获取并清洗A股日线数据

    symbol: 股票代码，如 '600519'
    start_date: 起始日期 '20200101'
    end_date: 截止日期 '20241231'
    adjust: 复权方式 'qfq'(前复权)/'hfq'(后复权)/''(不复权)
    """
    # 获取原始数据
    raw = ak.stock_zh_a_hist(
        symbol=symbol,
        period='daily',
        start_date=start_date,
        end_date=end_date,
        adjust=adjust
    )

    # 标准化列名
    raw = raw.rename(columns={
        '日期': 'date', '开盘': 'open', '收盘': 'close',
        '最高': 'high', '最低': 'low', '成交量': 'volume',
        '成交额': 'amount', '振幅': 'amplitude',
        '涨跌幅': 'pct_change', '涨跌额': 'change',
        '换手率': 'turnover'
    })

    # 设置日期索引并排序
    raw['date'] = pd.to_datetime(raw['date'])
    raw = raw.set_index('date').sort_index()

    # === 数据清洗流水线 ===
    df = raw.copy()
    n_original = len(df)

    # 1. 处理重复日期（取最后一条记录）
    df = df[~df.index.duplicated(keep='last')]

    # 2. 检测并标记极端价格错误
    # 价格突然翻倍或腰斩（在没有涨跌停限制的情况下）
    price_change = df['close'].pct_change()
    extreme_mask = price_change.abs() > 0.15  # 单日涨跌超15%可能是数据错误
    if extreme_mask.any():
        print(f"检测到 {extreme_mask.sum()} 个极端价格变动日:")
        for date in df.index[extreme_mask]:
            print(f"  {date.date()}: 变动={price_change[date]:.2%}")

    # 3. 处理零成交量日（停牌日）
    zero_volume = df['volume'] <= 0
    df.loc[zero_volume, ['open', 'high', 'low']] = df.loc[zero_volume, 'close'].values

    # 4. 前向填充（停牌延续最新价）
    # 注意：不建议在金融数据上使用插值，因为价格在停牌期间并没有"中间值"
    df['close'] = df['close'].ffill()
    df['open'] = df['open'].ffill()
    df['high'] = df['high'].ffill()
    df['low'] = df['low'].ffill()

    # 5. 衍生计算
    df['return'] = df['close'].pct_change()
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['range'] = (df['high'] - df['low']) / df['close']  # 日内振幅

    # 6. 标记异常收益率日（可能是脏数据或极端事件）
    ret_mean = df['return'].mean()
    ret_std = df['return'].std()
    df['is_abnormal'] = (df['return'] - ret_mean).abs() > 4 * ret_std

    # 7. 计算可用交易日数
    trading_days = (~zero_volume).sum()

    # === 数据质量报告 ===
    print("=" * 50)
    print(f"数据清洗报告: {symbol}")
    print("=" * 50)
    print(f"原始记录数: {n_original}")
    print(f"清洗后记录数: {len(df)}")
    print(f"重复日期: {n_original - len(df)}")
    print(f"零成交量日(停牌): {zero_volume.sum()} ({zero_volume.sum()/len(df):.1%})")
    print(f"异常收益率日: {df['is_abnormal'].sum()} ({df['is_abnormal'].sum()/len(df):.1%})")
    print(f"日期范围: {df.index.min().date()} ~ {df.index.max().date()}")
    print(f"实际交易日: {trading_days}")
    print(f"\n价格统计:")
    print(f"  开盘: {df['open'].min():.2f} ~ {df['open'].max():.2f}")
    print(f"  收盘: {df['close'].min():.2f} ~ {df['close'].max():.2f}")
    print(f"  日均成交量: {df.loc[~zero_volume, 'volume'].mean():,.0f}")

    return df
