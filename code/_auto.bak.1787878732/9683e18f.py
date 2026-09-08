# @quantlab/output: 9683e18f
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LassoCV, RidgeCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

def regularized_factor_selection(factors, returns, method='lasso', cv_splits=5):
    """
    完整的正则化因子选择流程

    factors: DataFrame, 每列是一个候选因子
    returns: Series, 未来一期收益率（目标变量）
    method: 'lasso', 'ridge', 'elastic_net'
    """
    # 数据清洗和对齐
    data = pd.concat([returns.rename('target'), factors], axis=1).dropna()
    y = data['target'].values
    X = data[factors.columns].values
    feature_names = factors.columns.tolist()

    # 标准化（正则化前必须标准化特征）
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 时序交叉验证（避免未来信息泄露）
    tscv = TimeSeriesSplit(n_splits=cv_splits)

    # 选择正则化方法
    if method == 'lasso':
        model = LassoCV(cv=tscv, max_iter=5000, random_state=42,
                        alphas=np.logspace(-4, 1, 50))
    elif method == 'ridge':
        model = RidgeCV(cv=tscv, alphas=np.logspace(-3, 3, 50))
    elif method == 'elastic_net':
        model = ElasticNetCV(cv=tscv, max_iter=5000, random_state=42,
                            l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9],
                            alphas=np.logspace(-4, 1, 20))

    model.fit(X_scaled, y)

    # 提取系数
    coef_df = pd.DataFrame({
        'factor': feature_names,
        'coefficient': model.coef_,
        'abs_coef': np.abs(model.coef_)
    }).sort_values('abs_coef', ascending=False)

    # 被选中的因子（Lasso/ElasticNet下系数不为0）
    if hasattr(model, 'l1_ratio_'):  # ElasticNet
        selected = coef_df[coef_df['coefficient'] != 0]
    elif method == 'lasso':
        selected = coef_df[coef_df['coefficient'] != 0]
    else:  # Ridge: 所有系数都非零，选绝对值最大的
        selected = coef_df[coef_df['abs_coef'] > coef_df['abs_coef'].quantile(0.5)]

    # 可视化
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 系数路径（仅Lasso/ElasticNet）
    if hasattr(model, 'mse_path_'):
        alphas = model.alphas_
        coef_path = model.coef_path_ if method == 'lasso' else None
        if coef_path is not None:
            for i in range(min(15, coef_path.shape[0])):
                axes[0].plot(alphas, coef_path[i], alpha=0.5, linewidth=0.8)
            axes[0].axvline(x=model.alpha_, color='red', linestyle='--',
                           label=f'最优α={model.alpha_:.4f}')
            axes[0].set_xscale('log')
            axes[0].set_xlabel('Alpha (正则化强度)')
            axes[0].set_ylabel('系数值')
            axes[0].set_title('Lasso系数路径')
            axes[0].legend()

    # 因子系数条形图
    top_n = min(20, len(coef_df))
    top_factors = coef_df.head(top_n)
    colors = ['steelblue' if c > 0 else 'coral' for c in top_factors['coefficient']]
    axes[1].barh(range(top_n), top_factors['coefficient'].values, color=colors)
    axes[1].set_yticks(range(top_n))
    axes[1].set_yticklabels(top_factors['factor'].values, fontsize=9)
    axes[1].axvline(x=0, color='black', linewidth=0.5)
    axes[1].set_xlabel('系数')
    axes[1].set_title(f'因子系数排名 (Top {top_n}, {method})')
    axes[1].invert_yaxis()

    # OLS诊断（用选中的因子做OLS，分析统计显著性）
    if len(selected) > 0 and len(selected) <= 15:
        X_selected = sm.add_constant(X_scaled[:, [feature_names.index(f) for f in selected['factor']]])
        ols_model = sm.OLS(y, X_selected).fit()

        coef_with_p = pd.DataFrame({
            '因子': ['Intercept'] + selected['factor'].tolist(),
            '系数': ols_model.params,
            't值': ols_model.tvalues,
            'p值': ols_model.pvalues
        })

        # 显著性可视化
        significant = coef_with_p['p值'] < 0.05
        axes[2].barh(range(len(coef_with_p)-1, -1, -1), coef_with_p['t值'].values,
                    color=['gray' if s else 'lightgray' for s in significant[::-1]])
        axes[2].axvline(x=0, color='black', linewidth=0.5)
        axes[2].axvline(x=1.96, color='red', linestyle='--', alpha=0.5, label='±1.96 (p=0.05)')
        axes[2].axvline(x=-1.96, color='red', linestyle='--', alpha=0.5)
        axes[2].set_yticks(range(len(coef_with_p)-1, -1, -1))
        axes[2].set_yticklabels(coef_with_p['因子'].values, fontsize=9)
        axes[2].set_xlabel('t统计量')
        axes[2].set_title('因子显著性 (OLS with selected factors)')
        axes[2].legend()
    else:
        axes[2].text(0.5, 0.5, '因子数量不适用OLS诊断',
                    ha='center', va='center', transform=axes[2].transAxes)

    plt.tight_layout()
    plt.show()

    # 输出结果
    print("=" * 60)
    print(f"正则化因子选择结果 ({method.upper()})")
    print("=" * 60)
    print(f"总候选因子数: {len(feature_names)}")
    print(f"选中因子数: {len(selected)}")
    if hasattr(model, 'alpha_'):
        print(f"最优正则化参数: {model.alpha_:.6f}")
    print(f"\n选中的因子及其系数:")
    for _, row in selected.iterrows():
        print(f"  {row['factor']:<25} {row['coefficient']:+.6f}")

    return {
        'model': model,
        'selected_factors': selected,
        'all_coefficients': coef_df,
        'scaler': scaler
    }

# 一键运行(用 demo 数据 factors(4列) + df['returns'] 作为预测目标)
_target = df['returns'].shift(-1).dropna()
_factor_set = factors.loc[_target.index]
results = regularized_factor_selection(_factor_set, _target, method='lasso', cv_splits=5)
print(f"\n✅ LASSO 选中 {len(results['selected_factors'])} 个因子 / 共 {len(_factor_set.columns)} 个候选")
print(f"✅ 有效因子列表: {results['selected_factors']['factor'].tolist()}")
