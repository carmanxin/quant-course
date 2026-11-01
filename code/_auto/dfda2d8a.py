# @quantlab/output: dfda2d8a
class CanaryReleaseManager:
    """金丝雀发布管理器"""

    def __init__(self, stages: list = None):
        if stages is None:
            self.stages = [
                {'pct': 0.01, 'min_days': 2, 'description': '1% canary'},
                {'pct': 0.05, 'min_days': 5, 'description': '5% expansion'},
                {'pct': 0.20, 'min_days': 7, 'description': '20% rollout'},
                {'pct': 0.50, 'min_days': 10, 'description': '50% rollout'},
                {'pct': 1.00, 'min_days': 14, 'description': '100% full'},
            ]
        else:
            self.stages = stages

        self.current_stage = 0
        self.days_in_stage = 0
        self.stage_metrics = []
        self.rollback_history = []

    def evaluate_promotion(self, daily_metrics: dict) -> dict:
        """
        评估是否可以推进到下一阶段

        Parameters
        ----------
        daily_metrics : dict
            包含 sharpe, max_drawdown, tracking_error, pnl 等指标
        """
        if self.current_stage >= len(self.stages) - 1:
            return {'action': 'COMPLETE', 'message': '已处于最终阶段'}

        current = self.stages[self.current_stage]
        self.days_in_stage += 1

        # 检查是否满足最低天数
        if self.days_in_stage < current['min_days']:
            return {
                'action': 'HOLD',
                'message': f"当前阶段需至少{current['min_days']}天，已运行{self.days_in_stage}天"
            }

        # 检查回撤是否在允许范围内
        if daily_metrics.get('drawdown_pct', 0) > 0.03:
            return {
                'action': 'ROLLBACK',
                'message': f"日内回撤{daily_metrics['drawdown_pct']:.2%}超过3%阈值，触发回滚"
            }

        # 检查累计 PnL
        if daily_metrics.get('cumulative_pnl', 0) < -0.02 * daily_metrics.get('allocated_capital', 1):
            return {
                'action': 'ROLLBACK',
                'message': '累计亏损超过分配资金的2%，触发回滚'
            }

        # 通过检查，推进到下一阶段
        self.current_stage += 1
        self.days_in_stage = 0

        next_stage = self.stages[self.current_stage]
        return {
            'action': 'PROMOTE',
            'message': f"推进到阶段{self.current_stage+1}: {next_stage['description']}",
            'new_allocation': next_stage['pct'],
            'current_stage': self.current_stage + 1
        }

    def trigger_rollback(self, reason: str) -> dict:
        """触发回滚"""
        rollback_info = {
            'from_stage': self.current_stage + 1,
            'to_stage': max(1, self.current_stage),  # 回到前一阶段，最低回到1%
            'reason': reason,
            'timestamp': pd.Timestamp.now()
        }

        self.rollback_history.append(rollback_info)
        self.current_stage = max(0, self.current_stage - 1)

        return rollback_info
