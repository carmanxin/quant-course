# @quantlab/output: 23fe1b3d
class PortfolioRebalancer:
    """组合再平衡器:支持固定周期 + 阈值触发两种模式"""

    def __init__(self, target_weights: np.ndarray, strategy_returns: pd.DataFrame,
                 rebalance_freq: str = 'M',  # 'D', 'W', 'M', 'Q'
                 threshold: float = 0.05):    # 5% 偏离阈值
        self.target_weights = target_weights
        self.returns = strategy_returns
        self.rebalance_freq = rebalance_freq
        self.threshold = threshold
        self.current_weights = target_weights.copy()
        self.rebalance_log = []
        self.equity = [1.0]
        self.weights_history = []

    def run(self) -> Tuple[pd.Series, pd.DataFrame]:
        """执行再平衡回测"""
        equity_curve = [1.0]
        weights_history = [self.current_weights.copy()]

        last_rebal_idx = 0
        for i in range(1, len(self.returns)):
            # 当日收益
            daily_ret = (self.returns.iloc[i] * self.current_weights).sum()
            equity_curve.append(equity_curve[-1] * (1 + daily_ret))

            # 更新当前权重
            new_w = self.current_weights * (1 + self.returns.iloc[i].values)
            new_w = new_w / new_w.sum()
            self.current_weights = new_w
            weights_history.append(new_w)

            # 检查是否需要再平衡
            deviation = np.abs(new_w - self.target_weights)
            days_since_last = i - last_rebal_idx

            # 触发条件 1:周期触发
            period_trigger = False
            if self.rebalance_freq == 'D':
                period_trigger = True
            elif self.rebalance_freq == 'W':
                period_trigger = (i % 5 == 0)
            elif self.rebalance_freq == 'M':
                period_trigger = (i % 21 == 0)

            # 触发条件 2:阈值触发
            threshold_trigger = deviation.max() > self.threshold

            if period_trigger or threshold_trigger:
                self.rebalance_log.append({
                    'date': self.returns.index[i],
                    'reason': 'period' if period_trigger else 'threshold',
                    'old_weights': self.current_weights.copy(),
                    'new_weights': self.target_weights.copy(),
                })
                self.current_weights = self.target_weights.copy()
                last_rebal_idx = i

        equity_series = pd.Series(equity_curve, index=self.returns.index[:len(equity_curve)])
        weights_df = pd.DataFrame(weights_history, index=self.returns.index)
        return equity_series, weights_df


def compare_rebalancing_methods():
    """比较固定周期再平衡 vs 阈值触发再平衡"""
    methods = {
        '不再平衡 (Buy & Hold)': None,
        '月度再平衡': PortfolioRebalancer(np.array([1/3]*3), returns_df, 'M', 0.05),
        '季度再平衡': PortfolioRebalancer(np.array([1/3]*3), returns_df, 'Q', 0.05),
        '阈值 5%': PortfolioRebalancer(np.array([1/3]*3), returns_df, 'NEVER', 0.05),
        '阈值 10%': PortfolioRebalancer(np.array([1/3]*3), returns_df, 'NEVER', 0.10),
    }

    print("=" * 70)
    print(f"{'方法':<25} {'年化收益':>10} {'夏普':>8} {'最大回撤':>10} {'再平衡次数':>10}")
    print("-" * 70)

    for name, engine in methods.items():
        if engine is None:
            # Buy & Hold
            p_ret = returns_df @ np.array([1/3]*3)
            ann_ret = p_ret.mean() * 252
            ann_vol = p_ret.std() * np.sqrt(252)
            sharpe = ann_ret / (ann_vol + 1e-9)
            eq = (1 + p_ret).cumprod()
            max_dd = (eq / eq.cummax() - 1).min()
            print(f"{name:<25} {ann_ret:>10.2%} {sharpe:>8.2f} {max_dd:>10.2%} {0:>10}")
        else:
            equity_curve, weights_df = engine.run()
            p_ret = equity_curve.pct_change().dropna()
            ann_ret = p_ret.mean() * 252
            ann_vol = p_ret.std() * np.sqrt(252)
            sharpe = ann_ret / (ann_vol + 1e-9)
            max_dd = (equity_curve / equity_curve.cummax() - 1).min()
            rebalances = len(engine.rebalance_log)
            print(f"{name:<25} {ann_ret:>10.2%} {sharpe:>8.2f} {max_dd:>10.2%} {rebalances:>10}")

compare_rebalancing_methods()
