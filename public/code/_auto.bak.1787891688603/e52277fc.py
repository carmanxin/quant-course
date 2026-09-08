# @quantlab/output: e52277fc
def factor_interaction_analysis(asset_returns: pd.DataFrame,
                                 macro_factors: pd.DataFrame,
                                 style_factors: pd.DataFrame) -> pd.DataFrame:
    """
    分析宏观因子与风格因子的交互效应。

    回归: r_i = α + β_macro * F_macro + β_style * F_style
               + γ * (F_macro * F_style) + ε

    参数:
        asset_returns: 资产收益率
        macro_factors: 宏观因子
        style_factors: 风格因子
    返回:
        交互项效应的DataFrame
    """
    results = []

    for macro_name in macro_factors.columns:
        for style_name in style_factors.columns:
            # 构造回归变量
            F_macro = macro_factors[macro_name].values
            F_style = style_factors[style_name].values
            F_interact = F_macro * F_style

            # 对每个资产做回归
            interaction_betas = []

            for asset in asset_returns.columns:
                y = asset_returns[asset].values
                X = np.column_stack([
                    np.ones(len(y)), F_macro, F_style, F_interact
                ])

                # 移除包含NaN的行
                mask = ~np.isnan(y) & ~np.isnan(X).any(axis=1)
                if mask.sum() < 10:
                    continue

                beta = np.linalg.lstsq(X[mask], y[mask], rcond=None)[0]
                interaction_betas.append(beta[3])  # 交互项系数

            if interaction_betas:
                mean_beta = np.mean(interaction_betas)
                t_stat = mean_beta / (np.std(interaction_betas) /
                                      np.sqrt(len(interaction_betas)))

                results.append({
                    'Macro_Factor': macro_name,
                    'Style_Factor': style_name,
                    'Interaction_Beta_mean': mean_beta,
                    't_stat': t_stat,
                    'Significant': abs(t_stat) > 1.96
                })

    return pd.DataFrame(results)
