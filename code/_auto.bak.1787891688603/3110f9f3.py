# @quantlab/output: 3110f9f3
class PolicyHistoricalBenchmark:
    """政策历史对标分析"""

    def __init__(self, historical_events: pd.DataFrame):
        """
        Parameters
        ----------
        historical_events : pd.DataFrame
            历史政策事件及市场反应数据库
            columns: ['event_date', 'event_name', 'theme', 'level',
                     'fiscal_amount', 'market_impact_1w', 'market_impact_1m',
                     'sector_impact_1w', 'sector_impact_1m']
        """
        self.history = historical_events

    def find_similar_events(self, current_event: dict, top_k: int = 3) -> pd.DataFrame:
        """
        找到历史上最相似的K个政策事件

        Parameters
        ----------
        current_event : dict
            {'theme': str, 'level': int, 'fiscal_amount': float, ...}
        top_k : int
            返回的相似事件数量
        """
        history = self.history.copy()

        # 同一主题
        same_theme = history[history['theme'] == current_event['theme']]
        if len(same_theme) < top_k:
            # 如果同主题事件不够，放宽到所有事件
            same_theme = history.copy()

        # 相似度计算（基于层级和财政力度）
        same_theme['similarity'] = 1.0

        # 层级接近度
        if 'level' in current_event:
            level_diff = abs(same_theme['level'] - current_event['level'])
            same_theme['similarity'] *= np.exp(-0.5 * level_diff)

        # 财政力度接近度
        if 'fiscal_amount' in current_event and current_event['fiscal_amount'] > 0:
            fiscal_ratio = np.minimum(
                same_theme['fiscal_amount'] / current_event['fiscal_amount'],
                current_event['fiscal_amount'] / same_theme['fiscal_amount'].replace(0, np.nan)
            ).fillna(0)
            same_theme['similarity'] *= fiscal_ratio

        return same_theme.nlargest(top_k, 'similarity')

    def estimate_market_impact(self, current_event: dict) -> dict:
        """
        基于历史对标估计当前政策的市场影响

        Returns
        -------
        dict : 包含预期影响范围（乐观/基准/悲观）
        """
        similar = self.find_similar_events(current_event, top_k=5)

        if len(similar) == 0:
            return {'has_benchmark': False, 'message': '没有足够的历史参考事件'}

        # 相似度加权平均
        weights = similar['similarity'] / similar['similarity'].sum()

        avg_impact_1w = (similar['market_impact_1w'] * weights).sum()
        avg_impact_1m = (similar['market_impact_1m'] * weights).sum()

        # 波动率加权（历史上不同事件的离散程度作为不确定性度量）
        std_impact_1w = np.sqrt(
            (similar['similarity'] * (similar['market_impact_1w'] - avg_impact_1w) ** 2).sum() /
            similar['similarity'].sum()
        )

        return {
            'has_benchmark': True,
            'n_similar_events': len(similar),
            'avg_impact_1w': avg_impact_1w,
            'avg_impact_1m': avg_impact_1m,
            'impact_std_1w': std_impact_1w,
            'optimistic_1w': avg_impact_1w + 1.96 * std_impact_1w,
            'pessimistic_1w': avg_impact_1w - 1.96 * std_impact_1w,
            'best_match': similar.iloc[0]['event_name']
        }
