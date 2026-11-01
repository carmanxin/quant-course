# @quantlab/output: 6fac1d4f
def finbert_fed_sentiment(texts: list) -> np.ndarray:
    """
    使用 FinBERT 对 FOMC 文本进行深度情感分析。

    注意：需要安装 transformers 库和预训练模型。
    `pip install transformers torch`

    参数:
        texts: 文本列表（每段FOMC声明）
    返回:
        每段文本的情感得分（-1到1，正=鹰派，负=鸽派）
    """
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch

        model_name = "ProsusAI/finbert"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        scores = []
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt",
                               truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1)[0]

            # FinBERT: [positive, negative, neutral]
            # 映射到鹰鸽：正面市场情绪 ≈ 鸽派（宽松利好市场）
            finbert_score = probs[0].item() - probs[1].item()
            scores.append(finbert_score)

        return np.array(scores)

    except ImportError:
        print("请安装 transformers 库: pip install transformers torch")
        return np.zeros(len(texts))
