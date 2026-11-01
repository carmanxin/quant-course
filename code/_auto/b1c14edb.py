# @quantlab/output: b1c14edb
import websocket
import json

# 演示用 redis client（实际项目从连接池获取）
class FakeRedis:
    def set(self, key, value):
        print(f"  redis.set({key!r}, {value!r})")

r = FakeRedis()

def on_message(ws, message):
    """WebSocket 收到消息时的回调"""
    data = json.loads(message)
    r.set(data['symbol'], data['price'])

# 创建 WebSocketApp（演示模式，不实际 run_forever）
ws = websocket.WebSocketApp("wss://api.exchange.com/ws", on_message=on_message)
print("WebSocketApp 已创建:")
print(f"  URL: wss://api.exchange.com/ws")
print(f"  回调: on_message(ws, message) -> 解析 JSON 并写入 Redis")
print()
print("生产环境调用：")
print("  ws.run_forever()  # 阻塞运行，断线自动重连")
print()
print("模拟一条 tick:")
demo_message = '{"symbol": "AAPL", "price": 187.23}'
print(f"  收到消息: {demo_message}")
on_message(ws, demo_message)
