# @quantlab/output: 9be6016c
class RetirementDecisionFramework:
    """策略退役决策框架"""

    def __init__(self, strategy_returns: pd.Series, config: dict):
        self.returns = strategy_returns
        self.config = config
        self.signals = []

    def evaluate_quantitative_signals(self) -> dict:
        """评估定量退役信号"""
        detector = AlphaDecayDetector(self.returns)

        # 1. Alpha 衰减检测
        alpha_trend = detector.trend_in_alpha(window=60)

        # 2. 滚动夏普比率
        rolling_sharpe = detector.rolling_sharpe(window=60).dropna()
        recent_sharpe = rolling_sharpe.iloc[-20:].mean() if len(rolling_sharpe) >= 20 else 0
        hist_sharpe = rolling_sharpe.mean()

        # 3. 最近收益
        recent_returns_3m = self.returns.iloc[-63:].mean() * 63 if len(self.returns) >= 63 else 0
        recent_returns_6m = self.returns.iloc[-126:].mean() * 126 if len(self.returns) >= 126 else 0

        # 4. 最大回撤比较
        cumulative = self.returns.cumsum()
        running_max = cumulative.cummax()
        drawdown = cumulative - running_max

        current_drawdown = drawdown.iloc[-1]
        max_drawdown = drawdown.min()

        # 5. 波动率变化
        recent_vol = self.returns.iloc[-63:].std()
        hist_vol = self.returns.std()
        vol_change = (recent_vol / hist_vol - 1) if hist_vol > 0 else 0

        signals = {
            'alpha_decay': {
                'active': alpha_trend.get('significant_decay', False),
                'detail': alpha_trend,
                'weight': 0.30
            },
            'sharpe_deterioration': {
                'active': recent_sharpe < hist_sharpe * 0.5,
                'detail': {
                    'recent_sharpe_20d': recent_sharpe,
                    'historical_sharpe': hist_sharpe,
                    'ratio': recent_sharpe / hist_sharpe if hist_sharpe > 0 else 0
                },
                'weight': 0.25
            },
            'persistent_losses': {
                'active': recent_returns_3m < 0 and recent_returns_6m < 0,
                'detail': {
                    'return_3m': recent_returns_3m,
                    'return_6m': recent_returns_6m
                },
                'weight': 0.20
            },
            'deep_drawdown': {
                'active': current_drawdown < max_drawdown * 0.8 and current_drawdown < -0.05,
                'detail': {
                    'current_drawdown': current_drawdown,
                    'max_drawdown': max_drawdown,
                    'drawdown_ratio': current_drawdown / max_drawdown if max_drawdown < 0 else 0
                },
                'weight': 0.15
            },
            'volatility_shift': {
                'active': abs(vol_change) > 0.5,
                'detail': {
                    'recent_volatility': recent_vol,
                    'historical_volatility': hist_vol,
                    'change_pct': vol_change
                },
                'weight': 0.10
            }
        }

        # 计算综合得分（加权激活信号数）
        total_score = sum(
            s['weight'] for s in signals.values() if s['active']
        )

        return {
            'signals': signals,
            'total_score': total_score,
            'recommendation': self._interpret_score(total_score)
        }

    def _interpret_score(self, score: float) -> str:
        if score >= 0.6:
            return 'STRONG_RETIRE: 强烈建议退役'
        elif score >= 0.4:
            return 'CONSIDER_RETIRE: 考虑退役，建议启动定性评估'
        elif score >= 0.2:
            return 'MONITOR_CLOSE: 密切关注，暂不建议退役'
        else:
            return 'HEALTHY: 策略健康，继续运行'

    def evaluate_qualitative_factors(self) -> dict:
        """评估定性退役因素"""
        factors = [
            {
                'factor': '市场结构性变化',
                'question': '策略依赖的市场机制是否发生了不可逆的变化？',
                'weight': 0.25
            },
            {
                'factor': '竞争加剧',
                'question': '策略所在的赛道竞争是否显著加剧？是否有新的大规模资金进入？',
                'weight': 0.20
            },
            {
                'factor': '数据优势丧失',
                'question': '策略依赖的数据/信息优势是否已经丧失或被广泛复制？',
                'weight': 0.20
            },
            {
                'factor': '替代策略存在',
                'question': '是否有更优的替代策略可用于替换？替换的切换成本如何？',
                'weight': 0.15
            },
            {
                'factor': '团队能力匹配',
                'question': '团队是否仍然具备维护该策略所需的专业能力？',
                'weight': 0.10
            },
            {
                'factor': '合规与监管',
                'question': '策略是否面临新的合规或监管风险？',
                'weight': 0.10
            }
        ]
        return factors
