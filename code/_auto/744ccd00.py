# @quantlab/output: 744ccd00
import matplotlib.pyplot as plt

def analyze_vpin_signal(vpin: pd.Series, threshold: float = 0.8):
    """
    分析 VPIN 信号并给出预警。

    参数:
        vpin: VPIN 时间序列
        threshold: 毒性预警阈值
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # 上图：VPIN 走势
    axes[0].plot(vpin.index, vpin.values, color='darkblue', linewidth=0.8)
    axes[0].axhline(y=threshold, color='red', linestyle='--',
                    label=f'预警阈值 ({threshold})')
    axes[0].fill_between(vpin.index, threshold, vpin.values,
                          where=(vpin.values > threshold),
                          alpha=0.3, color='red')
    axes[0].set_ylabel('VPIN')
    axes[0].set_title('订单流毒性指标 (VPIN)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 下图：毒性级别分布直方图
    axes[1].hist(vpin.dropna(), bins=100, color='steelblue',
                 edgecolor='white', alpha=0.8)
    axes[1].axvline(x=threshold, color='red', linestyle='--')
    axes[1].set_xlabel('VPIN')
    axes[1].set_ylabel('频率')
    axes[1].set_title('VPIN 经验分布')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # 统计摘要
    exceed_ratio = (vpin > threshold).mean()
    print(f"VPIN 超过 {threshold} 的比例: {exceed_ratio:.2%}")
    print(f"VPIN 均值: {vpin.mean():.4f}")
    print(f"VPIN 标准差: {vpin.std():.4f}")
    print(f"VPIN 95% 分位数: {vpin.quantile(0.95):.4f}")
