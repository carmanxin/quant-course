# @quantlab/output: b5d73a95
import numpy as np
import pandas as pd

def simulate_satellite_parking_analysis(ticker, n_weeks=52):
    """
    模拟通过卫星图像分析零售商店停车场的车流量

    原理：停车场车辆数 -> 客流量 -> 销售收入估计
    """
    # 基础客流
    base_traffic = np.random.uniform(500, 2000)

    # 季节性（节假日高峰）
    weeks = np.arange(n_weeks)
    seasonal = 1 + 0.3 * np.sin(2 * np.pi * weeks / 52 - 4)

    # 趋势（公司扩张/收缩）
    trend = 1 + 0.001 * np.arange(n_weeks) * np.random.choice([-1, 1])

    # 噪声
    noise = np.random.normal(0, 0.05, n_weeks)

    traffic = base_traffic * seasonal * trend * np.exp(noise)

    # 转换为销售收入估计
    avg_spend_per_customer = 50  # 平均每位顾客消费50元
    estimated_revenue = traffic * avg_spend_per_customer * 7  # 周收入

    # 计算同比变化（作为Alpha信号）
    yoy_change = pd.Series(estimated_revenue).pct_change(periods=52)

    df = pd.DataFrame({
        'week': pd.date_range('2023-01-01', periods=n_weeks, freq='W'),
        'parking_traffic': traffic.astype(int),
        'estimated_revenue': estimated_revenue,
        'yoy_change': yoy_change,
    })

    print(f"卫星图像分析 - {ticker} 停车场客流:")
    print(f"  平均周客流: {traffic.mean():.0f} 辆")
    print(f"  平均周收入: ${estimated_revenue.mean():,.0f}")
    print(f"  同比变化范围: [{yoy_change.min():.1%}, {yoy_change.max():.1%}]")

    return df

# 模拟
traffic_data = simulate_satellite_parking_analysis('WMT')
print(f"\n信号示例（前5周）:")
print(traffic_data[['week', 'parking_traffic', 'yoy_change']].head().to_string(index=False))
