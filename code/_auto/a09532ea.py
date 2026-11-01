# @quantlab/output: a09532ea
import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime
from typing import Callable, Dict, Any
import logging

class WebSocketMarketDataFeed:
    """
    基于 WebSocket 的实时行情数据接入。

    适用于：加密货币交易所、部分券商 API。
    """

    def __init__(self,
                 ws_url: str,
                 symbols: list,
                 on_trade: Callable = None,
                 on_quote: Callable = None,
                 on_error: Callable = None,
                 reconnect_delay: float = 1.0,
                 max_reconnect_attempts: int = 10):
        """
        参数:
            ws_url: WebSocket 端点 URL
            symbols: 订阅的标的列表
            on_trade: 成交回调函数(trade_data: dict)
            on_quote: 报价回调函数(quote_data: dict)
            on_error: 错误回调函数(error: Exception)
            reconnect_delay: 重连间隔（秒）
            max_reconnect_attempts: 最大重连次数
        """
        self.ws_url = ws_url
        self.symbols = symbols
        self.on_trade = on_trade or self._default_handler
        self.on_quote = on_quote or self._default_handler
        self.on_error = on_error or (lambda e: logging.error(f"WebSocket Error: {e}"))
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts

        # 统计
        self.message_count = 0
        self.trade_count = 0
        self.quote_count = 0
        self.reconnect_count = 0

        # 各 symbol 的最新行情缓存
        self.latest_quotes: Dict[str, Dict[str, Any]] = {}
        self.latest_trades: Dict[str, Dict[str, Any]] = {}

    def _default_handler(self, data: dict):
        """默认处理：存储到缓存"""
        if data.get('type') == 'trade':
            self.latest_trades[data['symbol']] = data
            self.trade_count += 1
        elif data.get('type') == 'quote':
            self.latest_quotes[data['symbol']] = data
            self.quote_count += 1

        self.message_count += 1

    async def _subscribe(self, websocket):
        """发送订阅消息（根据具体交易所 API 实现）"""
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [f"{s.lower()}@trade" for s in self.symbols] +
                      [f"{s.lower()}@depth" for s in self.symbols],
            "id": 1
        }
        await websocket.send(json.dumps(subscribe_msg))
        logging.info(f"Subscribed to {len(self.symbols)} symbols")

    async def _message_parser(self, raw_message: str) -> dict:
        """
        解析原始 WebSocket 消息为标准化格式。

        此为简化示例，实际需根据具体数据源的格式适配。
        """
        try:
            msg = json.loads(raw_message)

            # 示例：将不同交易所的格式统一为标准格式
            if 'e' in msg and msg['e'] == 'trade':
                # Binance 成交格式
                return {
                    'type': 'trade',
                    'symbol': msg['s'],
                    'price': float(msg['p']),
                    'size': float(msg['q']),
                    'timestamp': datetime.fromtimestamp(msg['T'] / 1000),
                    'trade_id': msg['t'],
                    'is_buyer_maker': msg['m']
                }
            elif 'type' in msg and msg['type'] == 'ticker':
                # Coinbase 格式
                return {
                    'type': 'quote',
                    'symbol': msg['product_id'],
                    'bid': float(msg['best_bid']),
                    'ask': float(msg['best_ask']),
                    'bid_size': float(msg.get('best_bid_size', 0)),
                    'ask_size': float(msg.get('best_ask_size', 0)),
                    'timestamp': datetime.fromisoformat(
                        msg['time'].replace('Z', '+00:00')
                    )
                }
            else:
                return msg

        except json.JSONDecodeError:
            return {'type': 'unknown', 'raw': raw_message}
        except Exception as e:
            logging.error(f"Message parse error: {e}")
            return {'type': 'error', 'error': str(e)}

    async def _process_messages(self, websocket):
        """处理 WebSocket 消息流"""
        async for raw_message in websocket:
            try:
                parsed = await self._message_parser(raw_message)

                if parsed.get('type') == 'trade':
                    self.on_trade(parsed)
                elif parsed.get('type') == 'quote':
                    self.on_quote(parsed)

            except Exception as e:
                self.on_error(e)

    async def connect(self):
        """建立 WebSocket 连接并开始消费数据"""
        attempt = 0

        while attempt < self.max_reconnect_attempts:
            try:
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=2**24  # 16MB max message size
                ) as ws:
                    logging.info(f"Connected to {self.ws_url}")
                    attempt = 0  # 重置重连计数

                    await self._subscribe(ws)
                    await self._process_messages(ws)

            except websockets.ConnectionClosed as e:
                self.reconnect_count += 1
                attempt += 1
                logging.warning(f"Connection closed: {e}. "
                                f"Reconnect attempt {attempt}/{self.max_reconnect_attempts}")
                await asyncio.sleep(self.reconnect_delay * attempt)

            except Exception as e:
                self.on_error(e)
                attempt += 1
                await asyncio.sleep(self.reconnect_delay)

        logging.error("Max reconnect attempts reached. Giving up.")

    def get_statistics(self) -> dict:
        """获取数据统计"""
        return {
            'message_count': self.message_count,
            'trade_count': self.trade_count,
            'quote_count': self.quote_count,
            'reconnect_count': self.reconnect_count
        }
