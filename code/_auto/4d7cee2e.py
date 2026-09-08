# @quantlab/output: 4d7cee2e
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta

class NewsAlphaGenerator:
    """从新闻文本生成量化交易信号"""

    def __init__(self, sentiment_model=None, max_lookback_days=5):
        self.sentiment_model = sentiment_model  # FinBERT或类似情感分析器
        self.max_lookback = max_lookback_days
        self.news_store = defaultdict(list)

    def process_news_article(self, ticker, date, headline, body, source='unknown'):
        """处理单条新闻文章"""
        # 合并标题和正文（标题通常信息密度更高，可以加权）
        full_text = f"{headline}. {body}"

        # 情感分析（简化：随机模拟）
        sentiment = np.random.uniform(-1, 1)  # 实际应用中使用FinBERT

        self.news_store[ticker].append({
            'date': date,
            'headline': headline,
            'sentiment': sentiment,
            'source': source
        })

    def generate_signals(self, date):
        """为给定日期生成所有股票的交易信号"""
        signals = {}
        cutoff = date - timedelta(days=self.max_lookback)

        for ticker, articles in self.news_store.items():
            recent = [a for a in articles if cutoff <= a['date'] <= date]

            if not recent:
                continue

            sentiments = np.array([a['sentiment'] for a in recent])

            # 信号特征
            avg_sentiment = sentiments.mean()
            sentiment_volatility = sentiments.std()
            n_articles = len(recent)

            # 情感趋势（近期vs早期）
            if len(sentiments) >= 4:
                recent_avg = sentiments[-2:].mean()  # 最近2篇
                early_avg = sentiments[:2].mean()    # 最早2篇
                sentiment_momentum = recent_avg - early_avg
            else:
                sentiment_momentum = 0.0

            # 综合信号 = 平均情感 + 情感动量 + 文章数衰减
            news_intensity = min(np.log1p(n_articles) / np.log(2), 1.0)  # 取log，上限1
            composite_signal = (
                0.5 * avg_sentiment +
                0.3 * sentiment_momentum +
                0.2 * np.sign(avg_sentiment) * news_intensity
            )

            signals[ticker] = {
                'signal': composite_signal,
                'avg_sentiment': avg_sentiment,
                'sentiment_momentum': sentiment_momentum,
                'n_articles': n_articles,
                'volatility': sentiment_volatility
            }

        return signals

# 模拟测试
np.random.seed(42)
alpha_gen = NewsAlphaGenerator()

# 模拟一些新闻事件
tickers = ['AAPL', 'TSLA', 'NVDA', 'JPM']
dates = pd.date_range('2024-01-01', periods=20, freq='B')

for ticker in tickers:
    for date in dates:
        if np.random.random() < 0.4:  # 40%的交易日有新闻
            alpha_gen.process_news_article(
                ticker, date,
                headline=f"{ticker} 新闻标题 {date.date()}",
                body=f"新闻正文内容关于{ticker}...",
                source='financial_news'
            )

# 在某一天生成信号
signals = alpha_gen.generate_signals(dates[-1])
print("新闻情感信号生成:")
print(f"{'Ticker':<8} {'信号':>8} {'平均情感':>10} {'情感动量':>10} {'文章数':>8}")
print("-" * 50)
for ticker, signal_info in sorted(signals.items(), key=lambda x: x[1]['signal'], reverse=True):
    print(f"{ticker:<8} {signal_info['signal']:>8.3f} {signal_info['avg_sentiment']:>10.3f} "
          f"{signal_info['sentiment_momentum']:>10.3f} {signal_info['n_articles']:>8}")
