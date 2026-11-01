# @quantlab/output: f5866cfe
import numpy as np
import pandas as pd

from scipy.signal import savgol_filter
from statsmodels.tsa.filters.hp_filter import hpfilter

def decompose_economic_cycle(gdp_series: pd.Series,
                              method: str = 'hp',
                              hp_lambda: float = 1600) -> dict:
    """
    分解经济时间序列的趋势和周期成分。

    参数:
        gdp_series: 经济时间序列（如季度GDP）
        method: 分解方法 ('hp' 或 'savgol')
        hp_lambda: HP滤波的平滑参数（季度数据=1600，月度=129600）
    返回:
        包含 trend, cycle, cycle_std 的字典
    """
    if method == 'hp':
        cycle, trend = hpfilter(gdp_series, lamb=hp_lambda)
    elif method == 'savgol':
        # Savitzky-Golay 滤波作为趋势
        window = max(5, len(gdp_series) // 4)
        if window % 2 == 0:
            window += 1
        trend = pd.Series(
            savgol_filter(gdp_series.values, window, 2),
            index=gdp_series.index
        )
        cycle = gdp_series - trend
    else:
        raise ValueError(f"Unknown method: {method}")

    # 周期成分标准化
    cycle_standardized = (cycle - cycle.mean()) / cycle.std()

    return {
        'trend': trend,
        'cycle': cycle,
        'cycle_standardized': cycle_standardized,
        'current_gap': cycle.iloc[-1],
        'output_gap_pct': (cycle.iloc[-1] / trend.iloc[-1]) * 100
    }

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(13)
_gdp = pd.Series(np.linspace(100, 118, 60) + np.sin(np.linspace(0, 6 * np.pi, 60)) * 2
                 + np.random.randn(60) * 0.5,
                 index=pd.date_range('2012-03-01', periods=60, freq='QE'))
_cycle = decompose_economic_cycle(_gdp, method='hp')
for _k, _v in _cycle.items():
    print(f'--- {_k} ---')
    print(_v.tail() if hasattr(_v, 'tail') else _v)
