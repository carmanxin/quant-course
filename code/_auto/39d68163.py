# @quantlab/output: 39d68163
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict


class PolicySignalExtractor:
    """政策事件NLP信号提取器"""

    def __init__(self, keyword_dict: dict = None):
        self.keyword_dict = keyword_dict or POLICY_KEYWORD_DICT

    def extract_signal_from_text(self, text: str, publish_date: str,
                                  source_level: str = '部委') -> dict:
        """
        从单篇政策新闻中提取信号

        Parameters
        ----------
        text : str
            新闻全文
        publish_date : str
            发布日期
        source_level : str
            发布层级（'顶层'/'部委'/'监管'/'地方'）

        Returns
        -------
        dict : 包含各主题的信号强度和得分
        """
        level_scores = {'顶层': 5, '部委': 3, '监管': 2, '地方': 1}
        base_level = level_scores.get(source_level, 2)

        signals = {}

        for theme, keywords in self.keyword_dict.items():
            # 检查是否命中了该主题的核心词
            core_hits = [kw for kw in keywords['核心词'] if kw in text]
            if not core_hits:
                continue

            # 命中核心词，进一步判断利好/利空方向
            positive_count = sum(1 for kw in keywords['利好词'] if kw in text)
            negative_count = sum(1 for kw in keywords['利空词'] if kw in text)

            # 信号方向（-1到1之间）
            if positive_count + negative_count > 0:
                direction = (positive_count - negative_count) / (positive_count + negative_count)
            else:
                direction = 0  # 中性

            # 信号强度
            hit_intensity = len(core_hits) / len(keywords['核心词'])
            specificity = (positive_count + negative_count) / (
                len(keywords['利好词']) + len(keywords['利空词'])
            )

            # 综合得分
            score = base_level * hit_intensity * (0.5 + 0.5 * specificity) * \
                    abs(direction) * keywords['权重']
            score *= direction  # 带方向的得分

            signals[theme] = {
                'direction': direction,
                'score': score,
                'hit_keywords': core_hits,
                'positive_hits': positive_count,
                'negative_hits': negative_count
            }

        return {
            'date': publish_date,
            'source_level': source_level,
            'base_level_score': base_level,
            'signals': signals,
            'has_signal': len(signals) > 0
        }

    def aggregate_daily_signals(self, daily_articles: list) -> pd.DataFrame:
        """
        汇总每日所有政策新闻的信号

        Parameters
        ----------
        daily_articles : list of dict
            每日的多篇政策新闻，每篇包含 text, publish_date, source_level
        """
        # 逐篇提取信号
        all_signals = []
        for article in daily_articles:
            result = self.extract_signal_from_text(
                article['text'],
                article.get('publish_date'),
                article.get('source_level', '部委')
            )
            if result['has_signal']:
                all_signals.append(result)

        # 汇总各主题信号
        daily_summary = defaultdict(lambda: {'total_score': 0, 'article_count': 0,
                                               'avg_direction': 0})

        for signal in all_signals:
            for theme, theme_signal in signal['signals'].items():
                daily_summary[theme]['total_score'] += theme_signal['score']
                daily_summary[theme]['article_count'] += 1
                daily_summary[theme]['avg_direction'] += theme_signal['direction']

        # 计算平均
        for theme in daily_summary:
            if daily_summary[theme]['article_count'] > 0:
                daily_summary[theme]['avg_direction'] /= daily_summary[theme]['article_count']

        # 转为 DataFrame
        rows = []
        for theme, summary in daily_summary.items():
            rows.append({
                'theme': theme,
                'signal_score': summary['total_score'],
                'article_count': summary['article_count'],
                'avg_direction': summary['avg_direction'],
                'weight': self.keyword_dict.get(theme, {}).get('权重', 1.0)
            })

        df = pd.DataFrame(rows)
        if len(df) > 0:
            df['weighted_score'] = df['signal_score'] * df['weight']

        return df

    def build_signal_time_series(self, articles_df: pd.DataFrame) -> pd.DataFrame:
        """
        构建政策信号时间序列

        Parameters
        ----------
        articles_df : pd.DataFrame
            包含 date, text, source_level 列的数据
        """
        daily_signals = []

        for date, group in articles_df.groupby('date'):
            articles = group.to_dict('records')
            daily_df = self.aggregate_daily_signals(articles)
            if len(daily_df) > 0:
                daily_df['date'] = date
                daily_signals.append(daily_df)

        if not daily_signals:
            return pd.DataFrame()

        ts = pd.concat(daily_signals, ignore_index=True)

        # 构建各主题的得分时间序列
        pivot = ts.pivot(index='date', columns='theme', values='weighted_score').fillna(0)

        # 加入市场综合政策信号（所有主题加权得分之和）
        pivot['policy_composite'] = pivot.sum(axis=1)

        # 计算信号的移动平均（平滑噪声）
        for col in pivot.columns:
            pivot[f'{col}_ma5'] = pivot[col].rolling(5).mean()

        return pivot
