# @quantlab/output: 2ac2784b
from kafka import KafkaProducer
import json

# 待发送的行情 tick（真实场景由行情网关推送进来）
tick = {
    'symbol': '600519.SH',
    'price': 1688.0,
    'size': 100,
    'ts': '2024-06-14T09:30:01.123456',
}
payload = json.dumps(tick, ensure_ascii=False).encode('utf-8')

# max_block_ms=5000：连不上 broker 时 5 秒内失败，而不是干等默认超时
try:
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                             max_block_ms=5000, request_timeout_ms=5000)
    producer.send('market_data', value=payload)
    producer.flush()
    print(f"已发送到 topic=market_data: {payload.decode()}")
except Exception as _e:
    print(f"⚠ 未连接 Kafka broker(localhost:9092): {type(_e).__name__}")
    print("  本段演示的是发送内容的构造与序列化：")
    print(f"    topic = market_data")
    print(f"    value = {payload.decode()}")
    print(f"    字节数 = {len(payload)}")
    print("  实盘要点：acks='all' + 幂等生产者，避免行情漏发/重发。")
