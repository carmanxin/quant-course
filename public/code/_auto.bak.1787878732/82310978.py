# @quantlab/output: 82310978
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.outliers_influence import variance_inflation_factor
# 注:本案例纯 matplotlib + statsmodels, 不依赖 seaborn(浏览器沙箱不支持)。
import statsmodels.api as sm

def multicollinearity_diagnosis(factors_df, vif_threshold=10):
    """
    因子共线性诊断：计算VIF并可视化

    factors_df: 每列是一个因子
    """
    # 处理缺失值
    data = factors_df.dropna()
    feature_names = data.columns.tolist()

    # 添加常数项用于VIF计算
    X = sm.add_constant(data)

    # 计算VIF
    vif_data = []
    for i in range(X.shape[1]):
        try:
            vif = variance_inflation_factor(X.values, i)
            vif_data.append({'feature': X.columns[i], 'VIF': vif})
        except:
            vif_data.append({'feature': X.columns[i], 'VIF': np.inf})

    vif_df = pd.DataFrame(vif_data)

    # 排除常数项的VIF（通常很大，不相关）
    vif_features = vif_df[vif_df['feature'] != 'const'].sort_values('VIF', ascending=False)

    # 标记高VIF因子
    high_vif = vif_features[vif_features['VIF'] > vif_threshold]
    ok_vif = vif_features[vif_features['VIF'] <= vif_threshold]

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # VIF条形图
    all_vif = pd.concat([high_vif, ok_vif])
    colors = ['coral' if v > vif_threshold else 'steelblue' for v in all_vif['VIF']]
    axes[0].barh(range(len(all_vif)), all_vif['VIF'].values, color=colors)
    axes[0].set_yticks(range(len(all_vif)))
    axes[0].set_yticklabels(all_vif['feature'].values, fontsize=9)
    axes[0].axvline(x=vif_threshold, color='red', linestyle='--', linewidth=2,
                   label=f'阈值={vif_threshold}')
    axes[0].set_xlabel('VIF值')
    axes[0].set_title(f'因子VIF诊断 (高VIF={len(high_vif)}个)')
    axes[0].legend()
    axes[0].invert_yaxis()

    # 相关性热力图(纯 matplotlib, 无需 seaborn)
    # 先计算高VIF因子之间的相关性
    if len(high_vif) > 1:
        high_vif_names = high_vif['feature'].tolist()
        corr_high_vif = data[high_vif_names].corr()
        ax_h = axes[1]
        arr = corr_high_vif.values
        im = ax_h.imshow(arr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
        ax_h.set_xticks(range(len(high_vif_names)))
        ax_h.set_xticklabels(high_vif_names, rotation=45, ha='right', fontsize=9)
        ax_h.set_yticks(range(len(high_vif_names)))
        ax_h.set_yticklabels(high_vif_names, fontsize=9)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                v = arr[i, j]
                color = 'white' if abs(v) > 0.6 else 'black'
                ax_h.text(j, i, f'{v:.2f}', ha='center', va='center',
                          color=color, fontsize=9)
        cbar = plt.colorbar(im, ax=ax_h, fraction=0.046, pad=0.04)
        cbar.set_label('相关系数')
        ax_h.set_title('高VIF因子间的相关性')
    else:
        axes[1].text(0.5, 0.5, '没有足够的高VIF因子\n用于展示相关性',
                    ha='center', va='center', transform=axes[1].transAxes)

    plt.tight_layout()
    plt.show()

    # 打印诊断结果
    print("=" * 50)
    print("多重共线性诊断报告")
    print("=" * 50)
    print(f"因子总数: {len(feature_names)}")
    print(f"高VIF因子(VIF>{vif_threshold}): {len(high_vif)}个")

    if len(high_vif) > 0:
        print(f"\n高VIF因子列表:")
        for _, row in high_vif.iterrows():
            print(f"  {row['feature']:<25} VIF={row['VIF']:.1f}")

        print(f"\n建议：考虑删除以下因子或使用Ridge/Lasso回归")
        # 按VIF从高到低，迭代删除高VIF中最高的一个
        remaining = feature_names.copy()
        simplified = []
        while True:
            X_check = sm.add_constant(data[remaining])
            vifs = [variance_inflation_factor(X_check.values, i)
                   for i in range(1, X_check.shape[1])]
            max_vif_idx = np.argmax(vifs)
            if vifs[max_vif_idx] > vif_threshold:
                removed = remaining.pop(max_vif_idx)
                simplified.append(removed)
            else:
                break
        print(f" 简化后因子集合 ({len(remaining)}个): {remaining}")

    return {
        'vif_df': vif_features,
        'high_vif_factors': high_vif,
        'correlation_matrix': data.corr()
    }


# 一键运行(用 demo 数据 factors)
vif_results = multicollinearity_diagnosis(factors, vif_threshold=10)
print(f"\n✅ 总因子数: {len(vif_results['vif_df'])}")
print(f"⚠️  高VIF因子数: {len(vif_results['high_vif_factors'])}")
print(f"✅ 高VIF因子: {vif_results['high_vif_factors']['feature'].tolist() if len(vif_results['high_vif_factors']) else '(无)'}")
