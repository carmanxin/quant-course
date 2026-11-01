# @quantlab/output: f0777b2b
import asyncio

import json

import logging

import time

import zlib

from dataclasses import dataclass, asdict

from datetime import datetime

from typing import Dict, Optional, Callable, Set

from collections import defaultdict, deque

import threading



import websockets

import redis

import numpy as np



# ==================== 数据结构 ====================



@dataclass

class TickData:

    """标准化的行情Tick数据结构"""

    symbol: str

    timestamp: float          # Unix时间戳（秒，微秒精度）

    exchange: str             # 交易所代码

    last_price: float

    volume: int               # 累计成交量

    turnover: float           # 累计成交额

    bid_price: float

    ask_price: float

    bid_volume: int

    ask_volume: int

    # Level-2数据

    bid_levels: Optional[list] = None  # [(price, volume), ...]

    ask_levels: Optional[list] = None



    def to_json(self):

        return json.dumps(asdict(self))



# ==================== 行情接入层 ====================



class MarketDataIngestor:

    """多交易所行情接入器"""



    def __init__(self, redis_client: redis.Redis,

                 kafka_producer=None):

        self.redis = redis_client

        self.kafka = kafka_producer

        self.logger = logging.getLogger("ingestor")



        # 统计信息

        self.stats: Dict[str, dict] = defaultdict(lambda: {

            'ticks_received': 0,

            'ticks_dropped': 0,

            'last_tick_time': 0,

            'latency_window': deque(maxlen=100)

        })



        # 回调注册

        self.on_tick_callbacks: list = []



        # 行情缓存（用于快速查询）

        self.tick_cache: Dict[str, TickData] = {}



    def register_callback(self, callback: Callable):

        """注册Tick回调函数"""

        self.on_tick_callbacks.append(callback)



    async def connect_exchange(self, exchange_name: str, ws_url: str,

                               symbols: Set[str]):

        """连接交易所WebSocket行情"""

        self.logger.info(f"连接 {exchange_name} WebSocket: {ws_url}")



        retry_count = 0

        max_retries = 10



        while retry_count < max_retries:

            try:

                async with websockets.connect(ws_url, ping_interval=20) as ws:

                    self.logger.info(f"{exchange_name} 连接成功")

                    retry_count = 0



                    # 发送订阅请求

                    subscribe_msg = {

                        "method": "subscribe",

                        "params": list(symbols),

                        "id": int(time.time())

                    }

                    await ws.send(json.dumps(subscribe_msg))



                    # 接收行情

                    async for message in ws:

                        await self._process_message(exchange_name, message)



            except websockets.ConnectionClosed as e:

                retry_count += 1

                wait_time = min(2 ** retry_count, 60)

                self.logger.warning(

                    f"{exchange_name} 连接断开: {e}. "

                    f"{retry_count}/{max_retries} 次重试, 等待 {wait_time}s"

                )

                await asyncio.sleep(wait_time)

            except Exception as e:

                self.logger.error(f"{exchange_name} 异常: {e}", exc_info=True)

                await asyncio.sleep(5)



    async def _process_message(self, exchange: str, raw_message: str):

        """处理原始行情消息"""

        try:

            msg = json.loads(raw_message)



            # 转换为标准化格式

            tick = self._normalize_tick(exchange, msg)

            if tick is None:

                return



            receive_time = time.time()

            latency = receive_time - tick.timestamp

            self.stats[exchange]['latency_window'].append(latency)

            self.stats[exchange]['ticks_received'] += 1

            self.stats[exchange]['last_tick_time'] = receive_time



            # 更新缓存

            self.tick_cache[tick.symbol] = tick



            # 1. 写入Redis（最新行情缓存）

            self.redis.setex(

                f"tick:{tick.symbol}",

                300,  # 5分钟过期

                tick.to_json()

            )



            # 2. 推送到Redis Pub/Sub（事件通知）

            self.redis.publish(f"tick_channel:{tick.symbol}", tick.to_json())



            # 3. 发送到Kafka（持久化和消费）

            if self.kafka:

                self.kafka.send('market_ticks', tick.to_json().encode())



            # 4. 触发回调

            for callback in self.on_tick_callbacks:

                try:

                    callback(tick)

                except Exception as e:

                    self.logger.error(f"回调异常: {e}")



        except json.JSONDecodeError:

            self.stats[exchange]['ticks_dropped'] += 1

        except Exception as e:

            self.logger.error(f"处理消息异常: {e}")



    def _normalize_tick(self, exchange: str, raw: dict) -> Optional[TickData]:

        """将交易所原始消息转换为标准格式"""

        try:

            return TickData(

                symbol=raw.get('symbol', ''),

                timestamp=raw.get('timestamp', time.time()),

                exchange=exchange,

                last_price=raw.get('last_price', raw.get('price', 0)),

                volume=raw.get('volume', 0),

                turnover=raw.get('turnover', 0),

                bid_price=raw.get('bid_price', 0),

                ask_price=raw.get('ask_price', 0),

                bid_volume=raw.get('bid_volume', 0),

                ask_volume=raw.get('ask_volume', 0),

            )

        except Exception:

            return None



    def get_stats(self) -> dict:

        """获取统计信息"""

        result = {}

        for exchange, stats in self.stats.items():

            latencies = list(stats['latency_window'])

            result[exchange] = {

                'ticks_received': stats['ticks_received'],

                'ticks_dropped': stats['ticks_dropped'],

                'avg_latency_ms': np.mean(latencies) * 1000 if latencies else 0,

                'max_latency_ms': np.max(latencies) * 1000 if latencies else 0,

                'last_tick_age_s': time.time() - stats['last_tick_time']

            }

        return result



# ==================== 数据归档层 ====================



class TickArchiver:

    """Tick数据归档器 - 将实时行情写入持久化存储"""



    def __init__(self, redis_client: redis.Redis,

                 db_connection=None):

        self.redis = redis_client

        self.db = db_connection

        self.buffer: Dict[str, list] = defaultdict(list)

        self.buffer_lock = threading.Lock()

        self.flush_interval = 60  # 每60秒刷盘一次

        self.buffer_max_size = 10000



        # 启动定时刷盘线程

        self.flush_thread = threading.Thread(

            target=self._periodic_flush, daemon=True

        )

        self.flush_thread.start()



    def archive(self, tick: TickData):

        """归档一个Tick"""

        key = f"{tick.symbol}_{datetime.fromtimestamp(tick.timestamp).strftime('%Y%m%d')}"



        with self.buffer_lock:

            self.buffer[key].append(tick)



            # 缓冲区满了立即刷盘

            if len(self.buffer[key]) >= self.buffer_max_size:

                self._flush_key(key)



    def _flush_key(self, key: str):

        """刷盘一个键的数据"""

        if key not in self.buffer:

            return



        ticks = self.buffer.pop(key)



        # 1. 写入Parquet/CSV文件

        # 2. 写入ClickHouse/TDengine

        # 3. 更新Redis元数据（数据范围、行数等）



        logging.debug(f"刷盘 {key}: {len(ticks)} 条记录")



    def _periodic_flush(self):

        """定时刷盘"""

        while True:

            time.sleep(self.flush_interval)

            with self.buffer_lock:

                keys = list(self.buffer.keys())

            for key in keys:

                self._flush_key(key)



# ==================== 数据质量监控 ====================



class DataQualityMonitor:

    """数据质量实时监控"""



    def __init__(self):

        self.alert_thresholds = {

            'max_gap_seconds': 5.0,      # 行情断连超过5秒报警

            'max_stale_seconds': 1.0,     # 行情停滞超过1秒报警

            'price_change_pct': 0.10,     # 价格瞬跳超过10%报警

            'zero_volume_tolerance': 10,  # 连续0成交量Tick数

        }

        self.last_tick_time: Dict[str, float] = {}

        self.last_price: Dict[str, float] = {}

        self.zero_vol_count: Dict[str, int] = defaultdict(int)



    def check_tick(self, tick: TickData) -> list:

        """检查一条Tick，返回发现问题列表"""

        issues = []



        # 1. 检查行情断连

        last_time = self.last_tick_time.get(tick.symbol)

        if last_time is not None:

            gap = tick.timestamp - last_time

            if gap > self.alert_thresholds['max_gap_seconds']:

                issues.append(f"行情断连: {gap:.1f}秒无数据")



        # 2. 价格跳变检查

        last_price = self.last_price.get(tick.symbol)

        if last_price is not None and last_price > 0:

            pct_change = abs(tick.last_price - last_price) / last_price

            if pct_change > self.alert_thresholds['price_change_pct']:

                issues.append(f"价格跳变: {pct_change:.2%}")



        # 3. 成交量异常

        if tick.volume == 0:

            self.zero_vol_count[tick.symbol] += 1

        else:

            self.zero_vol_count[tick.symbol] = 0



        if self.zero_vol_count[tick.symbol] > self.alert_thresholds['zero_volume_tolerance']:

            issues.append(f"连续零成交量: {self.zero_vol_count[tick.symbol]}次")



        # 4. 买卖价差检查

        if tick.bid_price > 0 and tick.ask_price > 0:

            if tick.bid_price >= tick.ask_price:

                issues.append(f"价差异常: bid({tick.bid_price}) >= ask({tick.ask_price})")



        self.last_tick_time[tick.symbol] = tick.timestamp

        self.last_price[tick.symbol] = tick.last_price



        return issues



# ==================== 使用示例 ====================



async def main():

    logging.basicConfig(level=logging.INFO)



    # 初始化Redis

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)



    # 创建行情接入器

    ingestor = MarketDataIngestor(redis_client=r)



    # 添加数据质量监控回调

    quality_monitor = DataQualityMonitor()

    def quality_check_callback(tick):

        issues = quality_monitor.check_tick(tick)

        for issue in issues:

            logging.warning(f"[QUALITY] {tick.symbol}: {issue}")



    ingestor.register_callback(quality_check_callback)



    # 连接交易所（示例）

    symbols = {'AAPL', 'GOOGL', 'MSFT', 'TSLA'}

    await ingestor.connect_exchange(

        'Exchange_A',

        'wss://api.exchange-a.com/ws/v2/market',

        symbols

    )



# asyncio.run(main())  # 实际运行时取消注释

print("实时数据管道代码演示已就绪")

print("  组件: 行情接入(Ingestor) | 数据归档(Archiver) | 质量监控(Monitor)")
