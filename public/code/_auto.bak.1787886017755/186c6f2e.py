# @quantlab/output: 186c6f2e
def rolling_metrics(returns, window=252):
    """
    计算滚动窗口的夏普比率和最大回撤，评估策略表现的稳定性
    """
    rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
    rolling_dd = returns.rolling(window).apply(
        lambda x: (x.cumsum().cummax() - x.cumsum()).max()
    )

    return rolling_sharpe, rolling_dd

# 可视化滚动夏普
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(12, 10))
rolling_sharpe, rolling_dd = rolling_metrics(returns)

axes[0].plot(rolling_sharpe, label='Rolling Sharpe (1Y)')
axes[0].axhline(y=0, color='r', linestyle='--')
axes[0].axhline(y=1, color='g', linestyle='--')
axes[0].set_title('Rolling Sharpe Ratio')
axes[0].legend()

axes[1].fill_between(rolling_dd.index, 0, rolling_dd.values, color='red', alpha=0.3)
axes[1].set_title('Rolling Max Drawdown')
axes[1].invert_yaxis()

axes[2].plot((1 + returns).cumprod(), label='Cumulative Return')
axes[2].set_title('Cumulative Return')
axes[2].legend()

plt.tight_layout()
plt.show()
