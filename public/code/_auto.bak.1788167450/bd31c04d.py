# @quantlab/output: bd31c04d
class AttributionReportAutomation:
    """归因报告自动生成器"""

    def __init__(self, strategy_manager):
        self.strategy_manager = strategy_manager
        self.report_history = []

    def generate_daily_report(self, date: str):
        """生成每日归因简报"""
        # 获取当日策略收益和因子数据
        pass

    def generate_weekly_report(self) -> str:
        """生成周度归因深度报告"""
        report = {
            'period': 'Weekly',
            'strategies': {},
            'summary': {},
            'anomalies': [],
            'recommendations': []
        }

        for strategy_id, strategy in self.strategy_manager.get_active_strategies().items():
            # 运行 Brinson 分解
            brinson = BrinsonAttribution(
                strategy.weights, strategy.benchmark_weights,
                strategy.returns, strategy.benchmark_returns
            )

            # 运行因子归因
            factor_att = FactorAttribution(
                strategy.returns, self.strategy_manager.factor_returns
            )

            report['strategies'][strategy_id] = {
                'brinson': brinson.decompose(),
                'factor_exposures': factor_att.factor_exposure_decomposition(),
                'rolling_betas': factor_att.rolling_factor_attribution()
            }

        # 异常检测
        for sid, sreport in report['strategies'].items():
            rolling_betas = sreport['rolling_betas']
            # 计算最近的 z-score
            recent = rolling_betas.iloc[-1]
            hist_mean = rolling_betas.mean()
            hist_std = rolling_betas.std()
            z_scores = (recent - hist_mean) / hist_std

            for factor, z in z_scores.items():
                if abs(z) > 2.0:
                    report['anomalies'].append({
                        'strategy': sid,
                        'factor': factor,
                        'z_score': z,
                        'current_exposure': recent[factor],
                        'avg_exposure': hist_mean[factor]
                    })

        self.report_history.append(report)
        return report
