# @quantlab/output: 3d4304b1
class LatencyMonitor:
    """
    实时 ETL 管道的延迟监控。

    度量维度：
    1. 接入延迟：交易所生成时间 -> 本系统接收时间
    2. 处理延迟：接收时间 -> 标准化完成时间
    3. 发布延迟：标准化完成 -> 下游消费时间
    4. 端到端延迟：交易所生成 -> 策略引擎消费
    """

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self.ingest_latencies = []    # 接入延迟
        self.process_latencies = []   # 处理延迟
        self.publish_latencies = []   # 发布延迟
        self.e2e_latencies = []       # 端到端延迟
        self.message_counts = []      # 消息量

    def record(self,
               exchange_ts: int,      # 交易所时间戳（纳秒）
               arrival_ts: int,       # 本系统接收时间（纳秒）
               processed_ts: int,     # 处理完成时间（纳秒）
               consumed_ts: int = None):  # 下游消费时间（纳秒）
        """记录一条消息的延迟"""
        ingest_lat = (arrival_ts - exchange_ts) / 1e6  # 转为毫秒
        process_lat = (processed_ts - arrival_ts) / 1e6

        self.ingest_latencies.append(ingest_lat)
        self.process_latencies.append(process_lat)

        if consumed_ts is not None:
            pub_lat = (consumed_ts - processed_ts) / 1e6
            e2e_lat = (consumed_ts - exchange_ts) / 1e6
            self.publish_latencies.append(pub_lat)
            self.e2e_latencies.append(e2e_lat)

    def get_percentiles(self) -> dict:
        """获取延迟百分位数"""
        def safe_percentile(data, p):
            if not data:
                return None
            return np.percentile(data, p)

        return {
            'ingest_p50': safe_percentile(self.ingest_latencies, 50),
            'ingest_p99': safe_percentile(self.ingest_latencies, 99),
            'process_p50': safe_percentile(self.process_latencies, 50),
            'process_p99': safe_percentile(self.process_latencies, 99),
            'e2e_p50': safe_percentile(self.e2e_latencies, 50),
            'e2e_p99': safe_percentile(self.e2e_latencies, 99),
        }
