# @quantlab/output: 8.1-random-forest
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
np.random.seed(42)
n = 500
X = np.random.randn(n, 5)
y = (0.3 * X[:, 0] - 0.2 * X[:, 1] + 0.1 * X[:, 2] + np.random.randn(n) * 0.3) > 0
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
model.fit(X_train, y_train)
train_acc = accuracy_score(y_train, model.predict(X_train))
test_acc = accuracy_score(y_test, model.predict(X_test))
probs = model.predict_proba(X_test)[:, 1]
print(f'训练集准确率: {train_acc:.3f}')
print(f'测试集准确率: {test_acc:.3f}')
print(f'预测概率范围: [{probs.min():.3f}, {probs.max():.3f}]')
print(f'\n特征重要性:')
for i, imp in enumerate(model.feature_importances_):
    print(f'  Feature {i+1}: {imp:.4f}')
