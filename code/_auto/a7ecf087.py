# @quantlab/output: a7ecf087
def llm_factor_generation_example():
    """
    使用LLM自动生成候选因子代码

    实际应用中，可以通过API调用GPT-4/Claude等LLM，
    根据自然语言描述生成因子计算代码
    """

    prompt_template = """
    请根据以下因子描述，生成Python代码来计算这个量化因子:

    因子名称: {factor_name}
    因子描述: {description}
    数据变量: df (pandas DataFrame, columns包括: open, high, low, close, volume)

    要求:
    1. 返回一个pandas Series作为因子值
    2. 处理缺失值和异常值
    3. 在代码注释中说明计算逻辑
    """

    examples = [
        {
            'factor_name': 'Amihud非流动性',
            'description': '衡量股票的流动性不足程度，定义为日收益率的绝对值除以日成交金额的平均值。非流动性越高，交易成本越大。',
        },
        {
            'factor_name': '价格延迟因子',
            'description': '衡量价格对市场信息反应的延迟程度。将股票日收益率对同期和滞后N期的市场收益率做回归，计算滞后项回归系数之和占总回归系数的比例。',
        },
        {
            'factor_name': '日内动量',
            'description': '用开盘后第一个小时的收益率（开盘价到10:30的价格变化）预测最后一个小时的收益率（14:00到收盘的价格变化）。使用过去M天的数据进行统计。',
        }
    ]

    print("LLM辅助因子挖掘示例:")
    for ex in examples:
        print(f"\n  因子: {ex['factor_name']}")
        print(f"  描述: {ex['description']}")
        print(f"  [提示词已生成，调用LLM API即可获得因子代码]")

llm_factor_generation_example()
