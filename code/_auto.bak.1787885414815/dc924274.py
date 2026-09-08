# @quantlab/output: dc924274
from kafka import KafkaProducer, KafkaConsumer
import msgpack
import time

class KafkaTickPipeline:
    """
    基于 Kafka 的 Tick 数据流处理管道。

    Topic 设计:
    - raw.ticks.{exchange}      : 原始数据（直接接入）
    - normalized.ticks.{asset}   : 标准化数据（清洗后）
    - derived.bars.{interval}    : 聚合 K 线
    - alerts.anomaly             : 异常告警
    """

    def __init__(self, bootstrap_servers: list):
        self.bootstrap_servers = bootstrap_servers

        # Producer: 序列化用 msgpack（比 JSON 快 5-10x）
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: msgpack.packb(v, use_bin_type=True),
            compression_type='lz4',
            linger_ms=5,          # 批处理延迟
            batch_size=16384      # 批大小
        )

    def normalize_tick(self, raw_tick: dict, source: str) -> dict:
        """
        将不同来源的 Tick 数据标准化为统一 Schema。

        参数:
            raw_tick: 原始 tick 字典
            source: 数据来源标识（如 'binance', 'xtp', 'ctp'）
        返回:
            标准化的 tick 字典
        """
        # 统一 Schema 定义
        normalized = {
            'timestamp': None,
            'symbol': None,
            'exchange': None,
            'price': None,
            'size': None,
            'bid': None,
            'ask': None,
            'bid_size': None,
            'ask_size': None,
            'trade_condition': None,
            'source': source,
            'arrival_time': int(time.time() * 1e9)  # 本系统接收时间
        }

        # 按来源适配
        if source == 'binance':
            normalized['timestamp'] = raw_tick.get('T', 0)
            normalized['symbol'] = raw_tick.get('s', '')
            normalized['price'] = float(raw_tick.get('p', 0))
            normalized['size'] = float(raw_tick.get('q', 0))

        elif source == 'xtp':
            normalized['timestamp'] = raw_tick.get('data_time', 0)
            normalized['symbol'] = raw_tick.get('ticker', '')
            normalized['price'] = raw_tick.get('last_price', 0)
            normalized['size'] = raw_tick.get('qty', 0)
            normalized['bid'] = raw_tick.get('bid', [None])[0]
            normalized['ask'] = raw_tick.get('ask', [None])[0]

        # 数据质量检查
        if normalized['price'] is not None and normalized['price'] <= 0:
            return None  # 过滤无效价格

        return normalized

    def publish_normalized_tick(self, tick: dict, asset_class: str):
        """发布标准化 Tick 到 Kafka"""
        if tick is None:
            return

        topic = f"normalized.ticks.{asset_class}"
        key = tick['symbol'].encode('utf-8')

        self.producer.send(topic, key=key, value=tick)

    def close(self):
        self.producer.flush()
        self.producer.close()
