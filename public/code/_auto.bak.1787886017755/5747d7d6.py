# @quantlab/output: 5747d7d6
from xgboost import XGBClassifier
model = XGBClassifier()
model.fit(X_train, y_train)
probs = model.predict_proba(X_test)[:,1]
