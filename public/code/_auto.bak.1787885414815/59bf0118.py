# @quantlab/output: 59bf0118
from sklearn.linear_model import LassoCV
# 一键运行:demo 数据已自动注入 factors (4 因子) 与 df['returns'] (目标变量)
_target = df['returns'].shift(-1).dropna()       # 未来一期收益(最后一行 NaN, 丢掉)
_factor_set = factors.loc[_target.index]            # 对齐因子
X = _factor_set.values
y = _target.values

model = LassoCV(cv=5).fit(X, y)
selected = np.where(model.coef_ != 0)[0]
print(f"✅ 总候选因子数: {len(_factor_set.columns)}")
print(f"✅ Lasso 选中因子个数: {len(selected)}")
print(f"✅ 最优正则化参数 α: {model.alpha_:.6f}")
selected_names = [_factor_set.columns[i] for i in selected]
print(f"✅ 选中因子: {selected_names if selected_names else '(全部被剔除)'}")
