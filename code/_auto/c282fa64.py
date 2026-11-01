# @quantlab/output: c282fa64
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score

class AdversarialValidator:
    """对抗验证器 - 检测训练集与测试集的分布偏移"""

    def __init__(self, n_estimators=100, max_depth=5):
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=1,  # Windows 上避免 loky 嵌套并行的开销
        )

    def validate(self, X_train, X_test, cv=5):
        """
        执行对抗验证

        X_train: 训练集特征
        X_test: 测试集特征
        """
        n_train = len(X_train)
        n_test = len(X_test)

        # 合并数据并创建标签
        X_combined = pd.concat([X_train, X_test], axis=0, ignore_index=True)
        y = np.array([0] * n_train + [1] * n_test)

        # 交叉验证评估
        scores = cross_val_score(
            self.classifier, X_combined, y,
            cv=cv, scoring='roc_auc', n_jobs=1
        )

        auc_mean = scores.mean()
        auc_std = scores.std()

        # 解释结果
        if auc_mean < 0.55:
            assessment = "分布一致，无显著偏移"
        elif auc_mean < 0.60:
            assessment = "存在轻微分布偏移，建议关注"
        elif auc_mean < 0.70:
            assessment = "分布显著不一致，存在可能的过拟合风险"
        else:
            assessment = "分布严重不一致！很可能存在数据泄露或regime突变"

        return {
            'auc_mean': auc_mean,
            'auc_std': auc_std,
            'assessment': assessment,
            'passed': auc_mean < 0.60
        }

    def feature_drift_analysis(self, X_train, X_test):
        """
        分析每个特征在训练集和测试集之间的分布漂移
        """
        drift_scores = {}

        for col in X_train.columns:
            train_vals = X_train[col].dropna()
            test_vals = X_test[col].dropna()

            if len(train_vals) < 10 or len(test_vals) < 10:
                continue

            # Kolmogorov-Smirnov检验
            from scipy.stats import ks_2samp
            ks_stat, ks_pvalue = ks_2samp(train_vals, test_vals)

            # 均值偏移（以标准差为单位）
            mean_shift = abs(train_vals.mean() - test_vals.mean())
            pooled_std = np.sqrt((train_vals.var() + test_vals.var()) / 2)
            shift_std = mean_shift / pooled_std if pooled_std > 0 else 0

            drift_scores[col] = {
                'ks_statistic': ks_stat,
                'ks_pvalue': ks_pvalue,
                'mean_shift_sigma': shift_std,
                'drift_significant': ks_pvalue < 0.05
            }

        # 按漂移程度排序
        drift_df = pd.DataFrame(drift_scores).T
        drift_df = drift_df.sort_values('ks_statistic', ascending=False)

        return drift_df

# ===== 对抗验证示例 =====
np.random.seed(42)

# 场景1: 无数据泄露（训练和测试来自相同分布）
n_samples = 1000
X_train_clean = pd.DataFrame({
    'factor_1': np.random.randn(n_samples),
    'factor_2': np.random.randn(n_samples),
    'factor_3': np.random.randn(n_samples),
})
X_test_clean = pd.DataFrame({
    'factor_1': np.random.randn(500),
    'factor_2': np.random.randn(500),
    'factor_3': np.random.randn(500),
})

validator = AdversarialValidator()
result_clean = validator.validate(X_train_clean, X_test_clean)
print("场景1 - 无数据泄露:")
print(f"  AUC: {result_clean['auc_mean']:.3f} (+/- {result_clean['auc_std']:.3f})")
print(f"  评估: {result_clean['assessment']}")

# 场景2: 有数据泄露（测试集某一特征=训练集特征值+偏移）
X_test_leaked = X_test_clean.copy()
X_test_leaked['factor_1'] += 0.8  # 人为引入分布偏移

result_leaked = validator.validate(X_train_clean, X_test_leaked)
print(f"\n场景2 - 存在分布偏移:")
print(f"  AUC: {result_leaked['auc_mean']:.3f} (+/- {result_leaked['auc_std']:.3f})")
print(f"  评估: {result_leaked['assessment']}")

# 特征漂移分析
drift = validator.feature_drift_analysis(X_train_clean, X_test_leaked)
print(f"\n特征漂移分析:")
print(drift.to_string())
