# @quantlab/output: ab47f905
import numpy as np
from numpy.linalg import eig


def pca_from_scratch(X: np.ndarray, n_components: int = 2) -> dict:
    """
    手动实现 PCA

    Parameters
    ----------
    X : np.ndarray
        数据矩阵，shape (n_samples, n_features)
    n_components : int
        保留的主成分数量
    """
    n_samples = X.shape[0]

    # 1. 中心化
    X_centered = X - X.mean(axis=0)

    # 2. 协方差矩阵
    cov_matrix = X_centered.T @ X_centered / (n_samples - 1)

    # 3. 特征分解
    eigenvalues, eigenvectors = eig(cov_matrix)

    # 4. 按特征值降序排列
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx].real
    eigenvectors = eigenvectors[:, idx].real

    # 5. 投影到前 k 个主成分
    W = eigenvectors[:, :n_components]
    X_pca = X_centered @ W

    # 6. 方差解释比例
    explained_variance_ratio = eigenvalues[:n_components] / eigenvalues.sum()

    return {
        'transformed': X_pca,
        'components': W,
        'eigenvalues': eigenvalues[:n_components],
        'explained_variance_ratio': explained_variance_ratio
    }


# 测试PCA
np.random.seed(42)
X = np.random.randn(100, 5)
X[:, 1] = X[:, 0] * 0.8 + np.random.randn(100) * 0.2  # 添加相关性

result = pca_from_scratch(X, n_components=2)
print(f"前2个主成分的方差解释比例: {result['explained_variance_ratio']}")
print(f"累计解释: {result['explained_variance_ratio'].sum():.3f}")
