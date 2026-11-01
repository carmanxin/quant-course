# @quantlab/output: 8ffef95e
from sklearn.decomposition import PCA
pca = PCA(n_components=5)
principal_factors = pca.fit_transform(factor_matrix)
