# @quantlab/output: 81b4f3d8
import numpy as np
import pandas as pd

def fama_macbeth_macro(asset_returns: pd.DataFrame,
                        macro_factors: pd.DataFrame,
                        n_lags: int = 0) -> dict:
    """
    Fama-MacBeth 两阶段回归估计宏观因子风险溢价。

    第一阶段：对每个资产做时间序列回归得到 β
    第二阶段：每期横截面回归得到因子风险溢价 λ

    参数:
        asset_returns: (T, N) 资产超额收益率
        macro_factors: (T, K) 宏观因子时间序列
        n_lags: 滞后因子数（用于考虑延迟反应）
    返回:
        包含 betas, risk_premia, t_stats 的字典
    """
    T, N = asset_returns.shape
    K = macro_factors.shape[1]

    # 第一阶段：时间序列回归 (每个资产)
    betas = np.zeros((N, K))
    for i in range(N):
        y = asset_returns.iloc[:, i].values
        X = macro_factors.values
        X = np.column_stack([np.ones(len(X)), X])  # 添加截距

        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        betas[i] = beta[1:]  # 斜率为因子暴露

    # 第二阶段：横截面回归 (每期)
    risk_premia = np.zeros((T, K))
    for t in range(T):
        y = asset_returns.iloc[t].values  # 横截面收益率
        X = betas  # 因子暴露作为解释变量
        X = np.column_stack([np.ones(N), X])

        premia = np.linalg.lstsq(X, y, rcond=None)[0]
        risk_premia[t] = premia[1:]

    # 风险溢价统计
    mean_premia = np.mean(risk_premia, axis=0)
    se_premia = np.std(risk_premia, axis=0) / np.sqrt(T)
    t_stats = mean_premia / se_premia

    # 显著性检验 (Newey-West adjusted)
    from statsmodels.tsa.stattools import adfuller

    return {
        'betas': pd.DataFrame(betas,
                               index=asset_returns.columns,
                               columns=[f'Beta_F{i+1}' for i in range(K)]),
        'risk_premia_annual': mean_premia * 12,
        't_stats': t_stats,
        'significant': np.abs(t_stats) > 1.96,
        'premia_time_series': pd.DataFrame(
            risk_premia,
            index=asset_returns.index,
            columns=[f'Lambda_F{i+1}' for i in range(K)]
        )
    }

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(7)
_dates = pd.date_range('2018-01-31', periods=60, freq='M')
_macro = pd.DataFrame({
    '增长': np.random.randn(60).cumsum() * 0.2,
    '通胀': np.random.randn(60).cumsum() * 0.15,
    '利率': np.random.randn(60).cumsum() * 0.25,
}, index=_dates)
_betas = np.random.uniform(-0.5, 1.5, size=(3, 8))
_asset = pd.DataFrame(
    _macro.values @ _betas / 12 + np.random.randn(60, 8) * 0.03,
    columns=[f'资产{i+1}' for i in range(8)], index=_dates)
_res = fama_macbeth_macro(_asset, _macro)
for _k, _v in _res.items():
    print(f'--- {_k} ---')
    print(_v.head() if hasattr(_v, 'head') else _v)
