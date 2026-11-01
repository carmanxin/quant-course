# @quantlab/output: 0f8dab28
import re
import numpy as np
import pandas as pd
from collections import Counter

def build_fed_sentiment_lexicon() -> dict:
    """
    构建美联储政策文本情感词典。

    基于学术文献（如 Apel & Blix Grimaldi, 2014）构建的
    鹰派/鸽派措辞词典。
    """
    hawkish_terms = {
        'tighten': 1.5, 'inflationary': 1.5, 'overheating': 2.0,
        'upside risk': 2.0, 'price pressure': 1.5, 'above target': 1.5,
        'wage pressure': 1.0, 'capacity constraints': 1.0,
        'accommodation': -0.5,  # 减少宽松 = 鹰派
        'strong': 0.5, 'robust': 0.5, 'solid': 0.3,
        'tight labor market': 1.0, 'inflation expectations': 0.5
    }

    dovish_terms = {
        'ease': 1.5, 'slack': 1.5, 'below target': 1.5,
        'downside risk': 2.0, 'disinflation': 1.5, 'deflation': 2.5,
        'patient': 1.5, 'considerable time': 2.0, 'gradual': 1.0,
        'accommodative': 1.5, 'headwinds': 1.0, 'uncertainty': 1.0,
        'global slowdown': 1.5, 'financial conditions': 0.5,
        'moderate': 0.5, 'subdued': 1.0
    }

    return {'hawkish': hawkish_terms, 'dovish': dovish_terms}


def score_fomc_statement(text: str,
                          lexicon: dict = None) -> dict:
    """
    对FOMC声明文本进行鹰鸽打分。

    参数:
        text: FOMC 声明全文
        lexicon: 鹰鸽词典
    返回:
        包含 hawkish_score, dovish_score, net_score 的字典
    """
    if lexicon is None:
        lexicon = build_fed_sentiment_lexicon()

    text_lower = text.lower()

    hawkish_score = 0
    dovish_score = 0
    matched_terms = []

    # 搜索鹰派措辞
    for term, weight in lexicon['hawkish'].items():
        count = len(re.findall(re.escape(term), text_lower))
        if count > 0:
            hawkish_score += count * weight
            matched_terms.append({'term': term, 'direction': 'hawkish',
                                   'count': count, 'weight': weight})

    # 搜索鸽派措辞
    for term, weight in lexicon['dovish'].items():
        count = len(re.findall(re.escape(term), text_lower))
        if count > 0:
            dovish_score += count * weight
            matched_terms.append({'term': term, 'direction': 'dovish',
                                   'count': count, 'weight': weight})

    net_score = hawkish_score - dovish_score

    # 归一化（按文本长度）
    n_words = len(text_lower.split())
    normalized_score = net_score / (n_words / 100)  # 每100词的得分

    return {
        'hawkish_score': hawkish_score,
        'dovish_score': dovish_score,
        'net_score': net_score,
        'normalized_score': normalized_score,
        'sentiment': 'hawkish' if net_score > 0.2 else (
            'dovish' if net_score < -0.2 else 'neutral'
        ),
        'matched_terms': matched_terms
    }
