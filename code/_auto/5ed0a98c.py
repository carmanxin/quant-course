# @quantlab/output: 5ed0a98c
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


# ===== 演示：用合成的历史价格序列跑一遍情景映射 =====
# 真实使用时把 market_data 换成 Wind/Tushare/yfinance 拉下来的真实收盘价面板
np.random.seed(42)
dates = pd.date_range('2008-01-01', '2022-12-31', freq='B')
assets = ['A_Share_Equity', 'US_Equity', 'Gold', 'Treasury_Bond', 'Credit_Bond']

# 每个资产的正常期漂移与波动（年化）
params = {
    'A_Share_Equity': (0.06, 0.25),
    'US_Equity':      (0.08, 0.18),
    'Gold':           (0.04, 0.15),
    'Treasury_Bond':  (0.03, 0.05),
    'Credit_Bond':    (0.04, 0.08),
}
# 危机期的日度额外冲击（体现"股债金"在不同危机中的分化）
crisis_shock = {
    ('2008-09-01', '2009-03-09'): {'A_Share_Equity': -0.0035, 'US_Equity': -0.0050,
                                   'Gold': 0.0004, 'Treasury_Bond': 0.0006, 'Credit_Bond': -0.0018},
    ('2015-06-12', '2015-08-24'): {'A_Share_Equity': -0.0090, 'US_Equity': -0.0012,
                                   'Gold': 0.0002, 'Treasury_Bond': 0.0004, 'Credit_Bond': -0.0006},
    ('2020-02-19', '2020-03-23'): {'A_Share_Equity': -0.0040, 'US_Equity': -0.0090,
                                   'Gold': -0.0010, 'Treasury_Bond': 0.0010, 'Credit_Bond': -0.0030},
    ('2022-01-01', '2022-06-30'): {'A_Share_Equity': -0.0012, 'US_Equity': -0.0018,
                                   'Gold': -0.0002, 'Treasury_Bond': -0.0008, 'Credit_Bond': -0.0010},
}

price_data = {}
for asset in assets:
    mu, vol = params[asset]
    daily = np.random.normal(mu / 252, vol / np.sqrt(252), len(dates))
    ret = pd.Series(daily, index=dates)
    for (s, e), shocks in crisis_shock.items():
        mask = (ret.index >= s) & (ret.index <= e)
        ret[mask] += shocks[asset]
    price_data[asset] = 100 * (1 + ret).cumprod()
market_data = pd.DataFrame(price_data)

holdings = {
    'A_Share_Equity': 40_000_000,
    'US_Equity':      25_000_000,
    'Gold':           10_000_000,
    'Treasury_Bond':  15_000_000,
    'Credit_Bond':    10_000_000,
}

stress = historical_scenario_analysis(holdings, market_data)

print(f"组合总市值: {sum(holdings.values()):,.0f} 元\n")
print("历史情景重演下的组合损益（按损失从大到小）:")
print("-" * 76)
print(f"{'情景':<18}{'区间':<26}{'损益(万元)':>14}{'损益%':>9}{'最大贡献资产':>16}")
print("-" * 76)
for _, row in stress.iterrows():
    print(f"{row['Scenario']:<18}{row['Period']:<26}"
          f"{row['Portfolio_Loss'] / 1e4:>13,.0f}{row['Loss_Pct']:>9.2f}{row['Worst_Asset']:>18}")

worst = stress.iloc[0]
print(f"\n最坏情景: {worst['Scenario']}，损失 {abs(worst['Portfolio_Loss']) / 1e4:,.0f} 万元"
      f"（{worst['Loss_Pct']:.2f}%）")
print("各资产贡献拆解:")
for asset, contrib in sorted(worst['Asset_Contributions'].items(), key=lambda kv: kv[1]):
    print(f"  {asset:<18}{contrib / 1e4:>12,.0f} 万元")
print("\n注：2010 闪崩只有单日数据（len<2），函数按设计自动跳过。")
