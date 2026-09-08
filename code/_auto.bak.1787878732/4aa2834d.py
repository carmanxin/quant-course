# @quantlab/output: 4aa2834d
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 关键历史危机情景的定义
HISTORICAL_SCENARIOS = {
    '2008_Financial_Crisis': {
        'name': '2008 全球金融危机',
        'period': ('2008-09-01', '2009-03-09'),
        'description': '雷曼兄弟破产引发的系统性危机'
    },
    '2010_Flash_Crash': {
        'name': '2010 闪崩',
        'period': ('2010-05-06', '2010-05-06'),
        'description': '算法交易引发的盘中闪崩'
    },
    '2011_EU_Debt_Crisis': {
        'name': '2011 欧债危机',
        'period': ('2011-07-01', '2011-10-04'),
        'description': '希腊债务危机蔓延，意大利西班牙国债收益率飙升'
    },
    '2015_China_Crash': {
        'name': '2015 中国股灾',
        'period': ('2015-06-12', '2015-08-24'),
        'description': 'A股去杠杆引发的暴跌'
    },
    '2020_COVID': {
        'name': '2020 新冠崩盘',
        'period': ('2020-02-19', '2020-03-23'),
        'description': '新冠疫情全球蔓延引发的流动性危机'
    },
    '2022_Rate_Hike': {
        'name': '2022 加息冲击',
        'period': ('2022-01-01', '2022-06-30'),
        'description': '美联储激进加息，股债双杀'
    }
}


def historical_scenario_analysis(portfolio_holdings: dict,
                                  market_data: pd.DataFrame,
                                  scenarios: list = None) -> pd.DataFrame:
    """
    将当前持仓映射到历史危机情景中，计算如果历史重演的组合损失。

    参数:
        portfolio_holdings: {资产名称: 持仓市值}
        market_data: 历史市场数据（价格序列）
        scenarios: 要测试的情景列表
    返回:
        各情景下的组合损失
    """
    if scenarios is None:
        scenarios = list(HISTORICAL_SCENARIOS.keys())

    results = []

    for scenario_key in scenarios:
        scenario = HISTORICAL_SCENARIOS[scenario_key]
        start, end = scenario['period']

        # 提取该期间的资产收益
        scenario_returns = market_data.loc[start:end]

        if len(scenario_returns) < 2:
            continue

        # 累计收益
        cumulative_returns = (scenario_returns.iloc[-1] /
                              scenario_returns.iloc[0] - 1)

        # 计算组合损失
        portfolio_loss = 0
        asset_contributions = {}
        for asset, position in portfolio_holdings.items():
            if asset in cumulative_returns.index:
                asset_loss = position * cumulative_returns[asset]
                portfolio_loss += asset_loss
                asset_contributions[asset] = asset_loss

        total_portfolio_value = sum(portfolio_holdings.values())

        results.append({
            'Scenario': scenario['name'],
            'Period': f"{start} to {end}",
            'Portfolio_Loss': portfolio_loss,
            'Loss_Pct': portfolio_loss / total_portfolio_value * 100,
            'Worst_Asset': max(asset_contributions,
                               key=lambda x: abs(asset_contributions[x])),
            'Asset_Contributions': asset_contributions
        })

    return pd.DataFrame(results).sort_values('Loss_Pct')
