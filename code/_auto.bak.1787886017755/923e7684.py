# @quantlab/output: 923e7684
import asyncio
from datetime import datetime, timedelta

class DataBackfiller:
    """数据回补器 - 在断连恢复后自动补齐缺失数据"""

    def __init__(self, redis_client, rest_api_client):
        self.redis = redis_client
        self.api = rest_api_client
        self.last_seq: Dict[str, int] = {}  # 每个标的的最后序号

    async def detect_and_backfill(self, symbol: str):
        """检测数据缺口并进行回补"""
        # 1. 从Redis获取最后一条缓存的Tick时间
        last_cached = self.redis.get(f"tick:{symbol}")
        if not last_cached:
            return

        last_tick = json.loads(last_cached)
        last_time = last_tick['timestamp']
        current_time = time.time()

        # 2. 如果超过一定时间没有新数据，触发回补
        gap_seconds = current_time - last_time
        if gap_seconds > 10:  # 超过10秒认为有缺口
            logging.warning(f"{symbol} 数据缺口: {gap_seconds:.1f}秒, 启动回补")

            # 3. 从REST API获取历史数据补上缺口
            missing_ticks = await self.api.get_historical_ticks(
                symbol=symbol,
                start_time=datetime.fromtimestamp(last_time),
                end_time=datetime.fromtimestamp(current_time)
            )

            # 4. 按时间顺序推送缺失的数据
            for tick in missing_ticks:
                self.redis.publish(f"tick_channel:{symbol}", json.dumps(tick))

            logging.info(f"{symbol} 回补完成: {len(missing_ticks)} 条记录")
            return len(missing_ticks)
        return 0
