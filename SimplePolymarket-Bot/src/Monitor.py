import json
import threading 
from websocket import WebSocketApp

class OrderBookMonitor:
    def __init__(self, market_tokens, threshold=0.005, executor_func=None):
        self.ws_url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
        self.market_tokens = market_tokens
        self.order_books = {}
        self.threshold = threshold
        self.executor_func = executor_func  # 套利执行器函数

    def on_open(self, ws):
        """连接建立时，发送订阅请求"""
        print("WebSocket Connected. Sending Subscriptions...")
        # 提取所有需要监控的 token_id
        all_token_ids = list(self.market_tokens.keys())
        
        # 构造订阅消息
        subscribe_msg = {
            "type": "subscribe",
            "assets_ids": all_token_ids,
            "channels": ["book"]  # 订阅订单簿频道
        }
        ws.send(json.dumps(subscribe_msg))
    # 处理推送消息
    def on_message(self, ws, message):
        """
        处理推送的价格信息
        """
        # ws: WebSocketApp实例
        data = json.loads(message) 
        # Polymarket会推送快照(Snapshot,全部订单)或更新(Update,价格变动)。代码要根据这些信息更新本地的order_books
        # 只要某个代币价格一变，立即触发check_arbitrage
        # Polymarket WS 返回的数据通常包含 'asset_id', 'asks', 'bids'
        # 我们只关注最优卖价 (Best Ask)
        asset_id = data.get('asset_id')
        asks = data.get('asks', [])

        if asset_id in self.market_tokens:
             # 获取当前最新的best Tokens
             best_ask = float(asks[0].get("price"))

             # 找到该token属于哪个市场及其类型(Yes/No)
             info = self.market_tokens[asset_id]
             m_id = info["market_id"]
             side = info["side"] # 'yes' 或 'no'

             # 更新本地账本
             if m_id not in self.order_books:
                 self.order_books[m_id] = {"Yes":None, "No":None}
             
             self.order_books[m_id][side] = best_ask

             # 尝试触发套利检查
             self.check_arbitrage(m_id)
    
    def check_arbitrage(self, market_id):
        """核心套利判定算法"""

        book = self.order_books.get(market_id)
        if not book or book["Yes"] is None or book["No"] is None:
            return

        total_cost = book["Yes"] + book["No"]

        if total_cost < 1 - self.threshold:
            print(f"🎯 ARBITRAGE DETECTED in Market {market_id}")
            print(f"   Yes: {book['Yes']:.4f}, No: {book['No']:.4f}, Total: {total_cost:.4f}")

            # 调用执行器函数
            if self.executor_func:
                self.executor_func(market_id, book["Yes"], book["No"])
            else:
                print("   ⚠️  未配置执行器函数")
        else:
            if Config.VERBOSE if 'Config' in globals() else False:
                print(f"Market {market_id} cost: {total_cost:.4f}")
    def on_error(self, ws, error):
        print(f"WS Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WS Closed")

    def start(self):
        """在独立线程中启动WebSocket"""
        self.ws = WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        # 运行连接
        self.ws.run_forever()

# --- 使用示例 ---
if __name__ == "__main__":
    # 映射表由gamma API代码生成
    mock_tokens = {
        "TOKEN_ID_FOR_YES":{"market_id": "M1", "side":"Yes"},
        "TOKEN_ID_FOR_NO":{"market_id": "M1", "side":"No"},
    }

    monitor = OrderBookMonitor(mock_tokens)
    monitor.start()