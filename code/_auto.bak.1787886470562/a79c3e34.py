# @quantlab/output: a79c3e34
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class FinancialSentimentAnalyzer:
    """使用FinBERT进行金融文本情感分析"""

    def __init__(self):
        model_name = "ProsusAI/finbert"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ['positive', 'negative', 'neutral']

    def analyze(self, text):
        """分析单条文本的情感"""
        inputs = self.tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=512, padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).numpy()[0]

        # 情感得分：正面 - 负面
        sentiment_score = probs[0] - probs[1]

        return {
            'text': text,
            'label': self.labels[np.argmax(probs)],
            'positive_prob': float(probs[0]),
            'negative_prob': float(probs[1]),
            'neutral_prob': float(probs[2]),
            'sentiment_score': float(sentiment_score)
        }

    def analyze_batch(self, texts):
        """批量分析多条文本"""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results

# 示例（不实际加载模型，演示接口）
print("FinBERT金融情感分析器:")
print("  输入: '公司第三季度营收同比增长30%，超出市场预期'")
print("  预期输出: 正面情感，得分 > 0\n")
print("  输入: '董事长因涉嫌内幕交易被证监会立案调查'")
print("  预期输出: 负面情感，得分 < 0\n")
print("  输入: '公司宣布将于下月召开年度股东大会'")
print("  预期输出: 中性情感，得分 ≈ 0")
