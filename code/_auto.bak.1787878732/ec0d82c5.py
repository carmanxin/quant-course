# @quantlab/output: ec0d82c5
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import arma_order_select_ic

def stationarity_diagnosis(series, max_lags=None):
    """
    全面诊断时间序列的平稳性特征
    """
    series = series.dropna()

    # ADF检验 (H0: 有单位根 = 非平稳)
    adf_stat, adf_p, adf_lags, adf_obs, adf_crit = adfuller(series, maxlag=max_lags, autolag='AIC')

    # KPSS检验 (H0: 序列是平稳的)
    kpss_stat, kpss_p, kpss_lags, kpss_crit = kpss(series, regression='c', nlags='auto')

    # 第一次差分
    diff1 = series.diff().dropna()
    adf_diff1_stat, adf_diff1_p, _, _, _ = adfuller(diff1, maxlag=max_lags, autolag='AIC')

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 原始序列
    axes[0, 0].plot(series.index, series.values)
    axes[0, 0].set_title(f'原始序列 (ADF p={adf_p:.4f}, KPSS p={kpss_p:.4f})')
    axes[0, 0].grid(True, alpha=0.3)

    # 一阶差分
    axes[0, 1].plot(diff1.index, diff1.values)
    axes[0, 1].set_title(f'一阶差分 (ADF p={adf_diff1_p:.4f})')
    axes[0, 1].grid(True, alpha=0.3)

    # ACF
    plot_acf(series, ax=axes[1, 0], lags=min(40, len(series)//4))
    axes[1, 0].set_title('自相关函数 (ACF)')

    # PACF
    plot_pacf(series, ax=axes[1, 1], lags=min(40, len(series)//4), method='ywm')
    axes[1, 1].set_title('偏自相关函数 (PACF)')

    plt.tight_layout()
    plt.show()

    # 输出诊断结果
    print("=" * 50)
    print("时间序列平稳性诊断")
    print("=" * 50)
    print(f"ADF检验: 统计量={adf_stat:.4f}, p值={adf_p:.4f}")
    print(f"  -> {'平稳 ✅' if adf_p < 0.05 else '非平稳 ❌ (存在单位根)'}")
    print(f"KPSS检验: 统计量={kpss_stat:.4f}, p值={kpss_p:.4f}")
    print(f"  -> {'平稳 ✅' if kpss_p > 0.05 else '非平稳 ❌'}")
    print(f"一阶差分后ADF p值: {adf_diff1_p:.4f}")

    # 综合判断
    if adf_p < 0.05 and kpss_p > 0.05:
        conclusion = "序列平稳（两种检验一致）"
    elif adf_p > 0.05 and kpss_p < 0.05:
        conclusion = "序列非平稳（两种检验一致），建议差分"
    else:
        conclusion = "检验结果不一致，谨慎判断"

    print(f"\n综合结论: {conclusion}")

    return {
        'adf_stat': adf_stat, 'adf_pvalue': adf_p,
        'kpss_stat': kpss_stat, 'kpss_pvalue': kpss_p,
        'diff_adf_pvalue': adf_diff1_p
    }


def auto_arima_model(series, max_p=5, max_d=2, max_q=5):
    """
    自动选择最优ARIMA模型（基于AIC）
    """
    series = series.dropna()

    best_aic = np.inf
    best_order = None
    best_model = None

    for d in range(max_d + 1):
        for p in range(max_p + 1):
            for q in range(max_q + 1):
                if p == 0 and q == 0:
                    continue
                try:
                    model = ARIMA(series, order=(p, d, q))
                    fitted = model.fit()
                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                        best_model = fitted
                except:
                    continue

    if best_model:
        print(f"最优模型: ARIMA{best_order}")
        print(f"AIC: {best_aic:.2f}")
        print(best_model.summary())

    return best_model, best_order


def garch_volatility_forecast(returns, p=1, q=1):
    """
    使用GARCH模型估计时变波动率

    需要安装: pip install arch
    """
    try:
        from arch import arch_model

        # 均值方程设为常数（收益率很难预测），重点在方差方程
        model = arch_model(returns * 100, vol='Garch', p=p, q=q, mean='Constant', dist='normal')
        fitted = model.fit(disp='off')

        # 条件波动率
        cond_vol = fitted.conditional_volatility / 100  # 转回小数

        # 预测
        forecast = fitted.forecast(horizon=22)  # 预测未来22个交易日
        forecast_vol = np.sqrt(forecast.variance.values[-1, :]) / 100

        print(fitted.summary())
        print(f"\n参数解读:")
        print(f"omega (基础波动): {fitted.params['omega']:.6f}")
        print(f"alpha (冲击敏感度): {fitted.params['alpha[1]']:.4f}")
        print(f"beta (波动持续性): {fitted.params['beta[1]']:.4f}")
        print(f"alpha+beta: {fitted.params['alpha[1]'] + fitted.params['beta[1]']:.4f} "
              + ('(接近1→长记忆性)' if fitted.params['alpha[1]'] + fitted.params['beta[1]'] > 0.95 else ''))

        return fitted, cond_vol, forecast_vol
    except ImportError:
        print("请先安装 arch 包: pip install arch")
        return None, None, None
