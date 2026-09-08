# @quantlab/output: d69d98d1
import websocket
def on_message(ws, message):
    data = json.loads(message)
    r.set(data['symbol'], data['price'])
ws = websocket.WebSocketApp("wss://api.exchange.com/ws", on_message=on_message)
ws.run_forever()
