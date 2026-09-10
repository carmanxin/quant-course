# @quantlab/output: 89a5fd8b
import numpy as np
import pandas as pd


def advanced_merge_operations():
    """量化中最常被追问的三个 DataFrame 合并/对齐场景。"""

    # ---------- 场景1：(date, code) 双键对齐，行情与因子的并集 ----------
    quotes = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-02', '2024-01-02', '2024-01-03', '2024-01-03']),
        'code': ['600519', '000001', '600519', '000001'],
        'close': [1680.0, 10.5, 1702.0, 10.4],
    })
    factors = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-02', '2024-01-03', '2024-01-03']),
        'code': ['600519', '600519', '300750'],   # 000001 缺因子，300750 缺行情
        'value': [0.82, 0.91, -0.35],
    })
    merged = quotes.merge(factors, on=['date', 'code'], how='outer')
    print("【场景1】(date, code) 外连接 —— 缺口一目了然")
    print(merged.to_string(index=False))
    print(f"  close 缺失 {merged['close'].isna().sum()} 行，"
          f"value 缺失 {merged['value'].isna().sum()} 行")
    # 因子按代码前值填充（注意先排序，且绝不能跨代码填充）
    merged['value_ffill'] = merged.sort_values('date').groupby('code')['value'].ffill()
    print(f"  按 code 分组 ffill 后 value 缺失降至 {merged['value_ffill'].isna().sum()} 行\n")

    # ---------- 场景2：merge_asof —— 委托时间戳配最近一笔行情 ----------
    orders = pd.DataFrame({
        'timestamp': pd.to_datetime(['2024-01-02 09:30:05', '2024-01-02 09:30:12',
                                     '2024-01-02 09:30:31']),
        'code': ['600519', '600519', '600519'],
        'side': ['BUY', 'SELL', 'BUY'],
    })
    prices = pd.DataFrame({
        'timestamp': pd.to_datetime(['2024-01-02 09:30:00', '2024-01-02 09:30:10',
                                     '2024-01-02 09:30:20', '2024-01-02 09:30:30']),
        'code': ['600519'] * 4,
        'price': [1680.0, 1681.5, 1680.8, 1682.2],
    })
    asof = pd.merge_asof(orders, prices, on='timestamp', by='code', direction='backward')
    print("【场景2】merge_asof(direction='backward') —— 只用委托时刻已知的行情")
    print(asof.to_string(index=False))
    print("  用 direction='forward' 就变成未来函数：拿到了下一笔还没发生的价格\n")

    # ---------- 场景3：截面标准化，transform 优于 apply ----------
    np.random.seed(7)
    panel = pd.DataFrame({
        'date': np.repeat(pd.to_datetime(['2024-01-02', '2024-01-03']), 4),
        'code': ['600519', '000001', '300750', '601318'] * 2,
        'factor': np.random.randn(8).round(3),
    })
    panel['z'] = panel.groupby('date')['factor'].transform(lambda x: (x - x.mean()) / x.std())
    print("【场景3】groupby.transform 做截面 z-score（形状不变，可直接赋列）")
    print(panel.to_string(index=False))
    chk = panel.groupby('date')['z'].agg(['mean', 'std']).round(6)
    print("  每个截面 z 的均值/标准差:")
    print(chk.to_string())
    print("  apply 返回的是嵌套结构，需要 reset_index 才能贴回原表 —— 这是面试常考的差别")

    return merged, asof, panel


advanced_merge_operations()
