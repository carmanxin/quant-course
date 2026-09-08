# @quantlab/output: 7f7037c7
from transformers import pipeline
sentiment = pipeline('sentiment-analysis')
result = sentiment("公司利润大幅增长")[0]
print(result['label'], result['score'])
