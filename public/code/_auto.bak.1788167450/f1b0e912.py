# @quantlab/output: f1b0e912
def advanced_merge_operations():
    """
    量化中常见的 DataFrame 合并场景
    """
    # 场景1：基于日期和代码的多索引合并
    # 处理股票代码缺失时用 fillna + bfill/ffill

    # 场景2：asof merge —— 找到最近的非精确匹配
    # pd.merge_asof(orders, prices, on='timestamp', by='code',
    #               direction='backward')

    # 场景3：截面操作 —— transform 优于 apply
    # df.groupby('date')['factor'].transform(lambda x: (x - x.mean()) / x.std())
    pass
