# @quantlab/output: a806b614
class PairsTradingStrategy:
    """配对交易策略原型实现"""

    def __init__(self, stock_a: pd.Series, stock_b: pd.Series,
                 lookback: int = 120, entry_z: float = 2.0,
                 exit_z: float = 0.5, stop_loss_z: float = 3.5):
        """
        Parameters
        ----------
        stock_a, stock_b : pd.Series
            两只股票的对数价格序列
        lookback : int
            用于估计回归参数的窗口
        entry_z : float
            入场Z-score阈值
        exit_z : float
            出场Z-score阈值
        stop_loss_z : float
            止损Z-score阈值（价差继续扩大）
        """
        self.log_a = np.log(stock_a)
        self.log_b = np.log(stock_b)
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_loss_z = stop_loss_z

    def compute_signals(self) -> pd.DataFrame:
        """生成交易信号"""
        signals = pd.DataFrame(index=self.log_a.index)

        for i in range(self.lookback, len(self.log_a)):
            # 滚动窗口内的回归
            y = self.log_a.iloc[i-self.lookback:i].values
            x = self.log_b.iloc[i-self.lookback:i].values
            X = np.column_stack([np.ones(len(x)), x])

            # OLS回归
            beta = np.linalg.lstsq(X, y, rcond=None)[0]

            # 当前价差
            spread = y[-1] - (beta[0] + beta[1] * x[-1])
            spread_mean = (y - (beta[0] + beta[1] * x)).mean()
            spread_std = (y - (beta[0] + beta[1] * x)).std()

            z_score = (spread - spread_mean) / spread_std if spread_std > 0 else 0

            signals.loc[signals.index[i], 'z_score'] = z_score
            signals.loc[signals.index[i], 'hedge_ratio'] = beta[1]
            signals.loc[signals.index[i], 'spread'] = spread

            # 信号生成
            if z_score > self.entry_z:
                signals.loc[signals.index[i], 'signal'] = -1  # 做空价差
            elif z_score < -self.entry_z:
                signals.loc[signals.index[i], 'signal'] = 1   # 做多价差
            elif abs(z_score) < self.exit_z:
                signals.loc[signals.index[i], 'signal'] = 0   # 平仓
            else:
                # 保持前一信号
                signals.loc[signals.index[i], 'signal'] = \
                    signals['signal'].iloc[i-1] if i > 0 else 0

        return signals
