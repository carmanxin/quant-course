# @quantlab/output: 88d1da36
import numpy as np
import pandas as pd

def orthogonalize_factors(factors_df, order='descending_variance'):
    """
    对因子进行正交化处理，消除因子间的线性重叠

    order: 正交化顺序
        - 'descending_variance'：按方差从大到小（常见做法）
    """
    data = factors_df.dropna()
    feature_names = data.columns.tolist()

    if order == 'descending_variance':
        variances = data.var()
        ordered_features = variances.sort_values(ascending=False).index.tolist()
    else:
        ordered_features = feature_names

    orthogonalized = pd.DataFrame(index=data.index)

    for i, feature in enumerate(ordered_features):
        y = data[feature].values
        if i == 0:
            orthogonalized[feature] = y
        else:
            # 将当前因子对前面的正交化因子回归，取残差
            X = orthogonalized[ordered_features[:i]].values
            beta = np.linalg.lstsq(X, y, rcond=None)[0]
            residuals = y - X @ beta
            orthogonalized[feature] = residuals

    return orthogonalized[feature_names]  # 按原始顺序返回

# 一键运行(用 demo 数据 factors)
ortho_factors = orthogonalize_factors(factors, order='descending_variance')
print(f"✅ 正交化前 因子总方差: {factors.var().sum():.4f}")
print(f"✅ 正交化后 因子总方差: {ortho_factors.var().sum():.4f}")
print(f"✅ 正交化后 列间最大相关系数: {np.abs(np.corrcoef(ortho_factors.T)).max():.4f} (理想值 ≈ 1.0,因为保留了每个因子的最大方差)")
