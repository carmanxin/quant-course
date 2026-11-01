# @quantlab/output: 2025bb06
import socket
from transformers import pipeline

def hf_reachable(host='huggingface.co', port=443, timeout=5):
    """预检 HuggingFace 是否可达：离线时(如 CI/内网)直接走演示结果，避免卡在下载重试。"""
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False

samples = [
    "公司利润大幅增长,业绩超出预期",
    "股价暴跌,投资者损失惨重",
    "未来发展存在不确定性",
]

if hf_reachable():
    sentiment = pipeline('sentiment-analysis',
                         model='uer/roberta-base-finetuned-dianping-chinese')
    print("情感分析(基于 RoBERTa 中文微调模型):")
    for s in samples:
        r = sentiment(s)[0]
        print(f"  [{r['label']:>5}] {r['score']:.3f}  {s}")
else:
    print("⚠ HuggingFace 不可达(离线/内网),改用演示用 mock 结果")
    mock = [("POSITIVE", 0.97, "公司利润大幅增长,业绩超出预期"),
            ("NEGATIVE", 0.93, "股价暴跌,投资者损失惨重"),
            ("NEUTRAL",  0.61, "未来发展存在不确定性")]
    for label, score, s in mock:
        print(f"  [{label:>5}] {score:.3f}  {s}")
