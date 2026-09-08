# @quantlab/output: 8b57ac8b
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def factor_risk_decomposition(weights: np.ndarray,
                                factor_exposures: np.ndarray,
                                factor_cov: np.ndarray,
                                specific_var: np.ndarray) -> dict:
    """
    将组合风险分解为因子风险和特异风险。

    参数:
        weights: (N,) 资产权重
        factor_exposures: (N, K) 因子暴露矩阵
        factor_cov: (K, K) 因子协方差矩阵
        specific_var: (N,) 各资产的特异方差
    返回:
        风险分解结果的字典
    """
    # 因子风险
    portfolio_factor_var = weights @ factor_exposures @ factor_cov @ \
                            factor_exposures.T @ weights

    # 特异风险
    D = np.diag(specific_var)
    portfolio_specific_var = weights @ D @ weights

    # 总风险
    total_var = portfolio_factor_var + portfolio_specific_var
    total_vol = np.sqrt(total_var)

    # 风险贡献分解
    cov_matrix = factor_exposures @ factor_cov @ factor_exposures.T + D
    portfolio_cov = cov_matrix @ weights

    # 边际风险贡献
    mrc = portfolio_cov / total_vol

    # 风险贡献
    rc = weights * mrc

    # 百分比风险贡献
    rc_pct = rc / total_vol * 100

    return {
        'total_volatility': total_vol,
        'factor_var': portfolio_factor_var,
        'specific_var': portfolio_specific_var,
        'factor_var_pct': portfolio_factor_var / total_var * 100,
        'specific_var_pct': portfolio_specific_var / total_var * 100,
        'marginal_risk_contribution': mrc,
        'risk_contribution': rc,
        'risk_contribution_pct': rc_pct
    }


def factor_level_risk_decomp(weights: np.ndarray,
                               factor_exposures: np.ndarray,
                               factor_cov: np.ndarray) -> pd.DataFrame:
    """
    将因子风险进一步分解到每个因子的贡献。

    参数:
        weights: (N,) 资产权重
        factor_exposures: (N, K) 因子暴露
        factor_cov: (K, K) 因子协方差
    返回:
        各因子的风险贡献DataFrame
    """
    portfolio_exposure = weights @ factor_exposures  # (K,) 组合因子暴露

    # 每个因子的方差贡献和协方差贡献
    factor_rc = np.zeros(len(portfolio_exposure))
    for k in range(len(portfolio_exposure)):
        factor_rc[k] = portfolio_exposure[k] * \
                       (factor_cov @ portfolio_exposure)[k]

    factor_rc_pct = factor_rc / np.sum(factor_rc) * 100

    return pd.DataFrame({
        'Factor': [f'F{i+1}' for i in range(len(factor_rc))],
        'Portfolio_Exposure': portfolio_exposure,
        'Risk_Contribution': factor_rc,
        'Risk_Contribution_Pct': factor_rc_pct
    }).sort_values('Risk_Contribution_Pct', ascending=False)
