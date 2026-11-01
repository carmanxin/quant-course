# @quantlab/output: 08e9412a
def yield_curve_pca(yield_changes):
    """
    收益率曲线变动的主成分分析
    yield_changes: DataFrame, shape (n_dates, n_maturities)
                   每行是每天各期限的收益率变动
    """
    # 协方差矩阵
    cov_matrix = np.cov(yield_changes.T)

    # 特征分解
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # 按特征值降序排列
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # 解释比例
    total_var = eigenvalues.sum()
    explained_ratio = eigenvalues / total_var

    print("PCA 结果:")
    for i in range(min(3, len(eigenvalues))):
        print(f"  PC{i+1}: {explained_ratio[i]*100:.1f}% 方差解释")
        print(f"  特征向量: {eigenvectors[:, i].round(3)}")

    return eigenvalues, eigenvectors, explained_ratio
