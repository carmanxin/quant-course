# @quantlab/output: 8b0abda6
import numpy as np
import pandas as pd

def tca_attribution(daily_executions, market_data):
    """
    TCA绩效归因：将每日执行成本分解为可归因的元素

    daily_executions: DataFrame, columns=['date', 'side', 'qty', 'price']
    market_data: DataFrame, columns=['date', 'spread_bp', 'volatility', 'adv']
    """
    df = daily_executions.merge(market_data, on='date')

    results = []
    for date, group in df.groupby('date'):
        for _, row in group.iterrows():
            # 价差成本：假设每次交易消耗半个价差
            spread_cost = row['spread_bp'] / 2

            # 波动率驱动的冲击
            participation = row['qty'] / row['adv']
            volatility_impact = row['volatility'] * np.sqrt(participation) * 0.5 * 10000

            # 总成本
            total_cost = spread_cost + volatility_impact

            results.append({
                'date': date,
                'side': row['side'],
                'qty': row['qty'],
                'spread_cost_bp': spread_cost,
                'impact_bp': volatility_impact,
                'total_cost_bp': total_cost
            })

    result_df = pd.DataFrame(results)

    # 按日期汇总
    daily_summary = result_df.groupby('date').agg({
        'spread_cost_bp': 'sum',
        'impact_bp': 'sum',
        'total_cost_bp': 'sum',
        'qty': 'sum'
    }).reset_index()

    # 计算成本比率
    daily_summary['spread_pct'] = daily_summary['spread_cost_bp'] / daily_summary['total_cost_bp'] * 100
    daily_summary['impact_pct'] = daily_summary['impact_bp'] / daily_summary['total_cost_bp'] * 100

    print("TCA成本归因分析:")
    print(f"{'日期':>12} {'成交量':>8} {'价差成本':>10} {'冲击成本':>10} "
          f"{'总成本':>10} {'价差占比':>8} {'冲击占比':>8}")
    print("-" * 70)
    for _, row in daily_summary.head(10).iterrows():
        print(f"{str(row['date']):>12} {row['qty']:>8,.0f} "
              f"{row['spread_cost_bp']:>10.1f} {row['impact_bp']:>10.1f} "
              f"{row['total_cost_bp']:>10.1f} {row['spread_pct']:>7.1f}% {row['impact_pct']:>7.1f}%")

    return daily_summary

# 示例数据
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=20, freq='B')
sample_data = pd.DataFrame({
    'date': np.repeat(dates, 3),
    'side': ['BUY', 'SELL', 'BUY'] * len(dates),
    'qty': np.random.randint(500, 5000, len(dates) * 3),
    'price': 100 + np.random.randn(len(dates) * 3) * 0.5
})
market = pd.DataFrame({
    'date': dates,
    'spread_bp': np.random.uniform(2, 8, len(dates)),
    'volatility': np.random.uniform(0.15, 0.35, len(dates)) / np.sqrt(252),
    'adv': [500000] * len(dates)
})

tca_attribution(sample_data, market)
