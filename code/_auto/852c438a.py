# @quantlab/output: 852c438a
import numpy as np
import pandas as pd

class PolicyEventDrivenStrategy:
    """政策事件驱动交易策略"""

    def __init__(self, signal_extractor: PolicySignalExtractor,
                 benchmark: PolicyHistoricalBenchmark,
                 sector_mapping: dict):
        """
        Parameters
        ----------
        sector_mapping : dict
            政策主题到申万行业的映射
            例如: {'新能源': ['电气设备', '有色金属'], '半导体': ['电子']}
        """
        self.extractor = signal_extractor
        self.benchmark = benchmark
        self.sector_mapping = sector_mapping

    def on_policy_event(self, event_articles: list, market_data: pd.DataFrame) -> dict:
        """
        政策事件发生时的交易决策

        Returns
        -------
        dict : 包含调仓建议
        """
        # 1. 提取政策信号
        daily_signals = self.extractor.aggregate_daily_signals(event_articles)

        if len(daily_signals) == 0:
            return {'action': 'NO_ACTION', 'reason': '无有效政策信号'}

        # 2. 识别信号最强的主题
        top_signal = daily_signals.loc[
            daily_signals['weighted_score'].abs().nlargest(1).index[0]
        ]

        theme = top_signal['theme']
        direction = top_signal['avg_direction']
        score = top_signal['weighted_score']

        # 3. 历史对标
        benchmark_result = self.benchmark.estimate_market_impact({
            'theme': theme,
            'level': 3,  # 默认部委级别
            'fiscal_amount': abs(score) * 100  # 近似估计
        })

        # 4. 确定交易方向
        if direction > 0.3 and score > 0:
            action = 'OVERWEIGHT'
        elif direction < -0.3 and score < 0:
            action = 'UNDERWEIGHT'
        else:
            action = 'NEUTRAL'

        # 5. 映射到行业
        target_sectors = self.sector_mapping.get(theme, [])

        if not target_sectors:
            return {'action': 'NO_ACTION', 'reason': f'主题 {theme} 无行业映射'}

        # 6. 计算仓位调整幅度
        if benchmark_result.get('has_benchmark'):
            # 基于历史影响的置信区间
            position_size = min(0.15, 0.05 + abs(benchmark_result['avg_impact_1w']) * 5)
        else:
            # 默认仓位
            position_size = 0.05

        return {
            'action': action,
            'theme': theme,
            'direction': direction,
            'signal_score': score,
            'target_sectors': target_sectors,
            'position_size': position_size,
            'benchmark': benchmark_result,
            'entry_date': datetime.now().strftime('%Y-%m-%d'),
            'expected_holding_period': '1-4 weeks'
        }

    def compute_policy_sentiment_index(self, signal_ts: pd.DataFrame) -> pd.Series:
        """
        计算政策情绪指数

        综合各主题政策信号的市场整体情绪代理变量
        """
        if 'policy_composite_ma5' in signal_ts.columns:
            sentiment = signal_ts['policy_composite_ma5']

            # 标准化到 -1 到 1 之间
            sentiment_normalized = 2 * (sentiment - sentiment.min()) / \
                                   (sentiment.max() - sentiment.min()) - 1

            return sentiment_normalized

        return pd.Series(name='policy_sentiment')

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
np.random.seed(151)
_ext = PolicySignalExtractor()
_hist = pd.DataFrame([
    {'event_name': '新能源产业规划', 'theme': '新能源', 'level': '国务院', 'fiscal_amount': 3e11, 'market_impact_1w': 0.05, 'market_impact_1m': 0.12},
])
_bench = PolicyHistoricalBenchmark(_hist)
_sect_map = {'新能源': ['光伏', '锂电', '风电'], '货币宽松': ['银行', '券商']}
_strat = PolicyEventDrivenStrategy(_ext, _bench, _sect_map)
_articles = [{'text': '国务院出台新能源车消费补贴政策', 'publish_date': '2024-06-01', 'source_level': '国务院'},
             {'text': '多部委联合印发储能产业支持方案', 'publish_date': '2024-06-02', 'source_level': '部委'}]
_mkt = pd.DataFrame({'close': np.linspace(100, 104, 10)},
                    index=pd.date_range('2024-05-30', periods=10))
try:
    print('事件响应:', _strat.on_policy_event(_articles, _mkt))
except Exception:
    pass
try:
    _ts = _strat.compute_policy_sentiment_index(pd.DataFrame({'score': [0.6, 0.8, 0.4, 0.5]},
        index=pd.date_range('2024-06-01', periods=4)))
    print('政策情绪指数:', _ts if not hasattr(_ts, 'tail') else _ts.tail())
except Exception:
    pass
