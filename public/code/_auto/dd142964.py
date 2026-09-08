# @quantlab/output: dd142964
import re
from collections import Counter

class LMFinancialSentiment:
    """基于Loughran-McDonald词典的金融情感分析"""

    def __init__(self):
        # 简化版Loughran-McDonald词典（实际使用时应加载完整词典文件）
        self.positive_words = {
            'profit', 'growth', 'increase', 'gain', 'strong', 'positive',
            'improve', 'success', 'opportunity', 'record', 'exceed',
            'achieve', 'optimistic', 'expansion', 'innovation', 'dividend',
            'upgrade', 'outperform', 'beat', 'momentum', 'synergy'
        }
        self.negative_words = {
            'loss', 'decline', 'decrease', 'weak', 'negative', 'risk',
            'failure', 'litigation', 'investigation', 'impairment', 'restructure',
            'downgrade', 'underperform', 'miss', 'uncertainty', 'volatility',
            'default', 'bankruptcy', 'layoff', 'write-down', 'penalty'
        }
        self.uncertainty_words = {
            'may', 'might', 'could', 'uncertain', 'possible', 'approximately',
            'estimate', 'likely', 'potential', 'pending', 'subject to',
            'believe', 'expect', 'anticipate', 'guidance', 'forecast'
        }
        self.litigious_words = {
            'lawsuit', 'litigation', 'allegation', 'dispute', 'court',
            'settlement', 'plaintiff', 'defendant', 'damages', 'ruling'
        }

    def analyze(self, text):
        """分析文本的L-M情感分数"""
        # 分词并清洗
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        word_counts = Counter(words)
        total_words = len(words)

        pos_count = sum(word_counts[w] for w in self.positive_words)
        neg_count = sum(word_counts[w] for w in self.negative_words)
        uncer_count = sum(word_counts[w] for w in self.uncertainty_words)
        litig_count = sum(word_counts[w] for w in self.litigious_words)

        # 情感分数（净正面词频，控制不确定性的影响）
        sentiment_score = (pos_count - neg_count) / max(total_words, 1)

        return {
            'positive_pct': pos_count / max(total_words, 1),
            'negative_pct': neg_count / max(total_words, 1),
            'uncertainty_pct': uncer_count / max(total_words, 1),
            'litigious_pct': litig_count / max(total_words, 1),
            'net_sentiment': sentiment_score,
            'total_words': total_words
        }

# 示例
analyzer = LMFinancialSentiment()

texts = [
    "The company reported record profit and strong revenue growth, exceeding analyst expectations.",
    "The company faces significant litigation risk and has announced major layoffs following the investigation.",
    "Management believes the restructuring may improve operational efficiency, though the outcome remains uncertain."
]

for i, text in enumerate(texts):
    result = analyzer.analyze(text)
    print(f"\n文本 {i+1}:")
    print(f"  {'正面词%':<12} {'负面词%':<12} {'不确定词%':<12} {'诉讼词%':<12} {'净情感':<10}")
    print(f"  {result['positive_pct']:>11.3f} {result['negative_pct']:>11.3f} "
          f"{result['uncertainty_pct']:>11.3f} {result['litigious_pct']:>11.3f} "
          f"{result['net_sentiment']:>9.4f}")
