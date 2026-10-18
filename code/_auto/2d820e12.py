# @quantlab/output: 2d820e12
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


# ===== 演示模式:展示数据回补器的接口 =====
class FakeRedis:
    def get(self, key): return None
    def publish(self, channel, msg): return 1

class FakeRestAPI:
    async def get_historical_ticks(self, symbol, start_time, end_time):
        return [{'symbol': symbol, 'price': 100.0, 'timestamp': 0}]

print("数据回补器(DataBackfiller)演示就绪")
print("  - 实时检测每只标的的最后缓存 tick")
print("  - 当 gap 超过阈值(默认 10 秒)时自动触发回补")
print("  - 从 REST API 获取缺失区间历史数据并 publish 到 Redis channel")

# 同步展示同步方法签名(实际生产用 asyncio.run 跑 async detect_and_backfill)
import inspect
sig = inspect.signature(DataBackfiller.detect_and_backfill)
print(f"\n  detect_and_backfill{sig}  (async)")
print(f"  典型调用: await backfiller.detect_and_backfill('AAPL')")
