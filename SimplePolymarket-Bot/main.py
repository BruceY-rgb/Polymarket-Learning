"""
Polymarket套利交易系统 - 主启动文件

该系统会：
1. 扫描活跃市场
2. 监控订单簿价格
3. 检测套利机会
4. 执行交易
"""

import sys
import signal
import threading
from typing import Dict, List
import json

# 导入项目模块
from src.config import Config
from src.Scanner import fetch_arbitrage_candidates, parse_market_metadata
from src.Monitor import OrderBookMonitor
from src.Executor import execute_arbitrage


class ArbitrageSystem:
    """套利交易系统主类"""

    def __init__(self):
        """初始化系统"""
        self.market_tokens: Dict[str, Dict] = {}
        self.monitor: OrderBookMonitor = None
        self.running = False

        print("=" * 60)
        print("🚀 Polymarket套利交易系统启动")
        print("=" * 60)

    def scan_markets(self) -> bool:
        """
        扫描市场并准备监控
        返回: 是否成功
        """
        try:
            print("\n📊 正在扫描活跃市场...")

            markets = fetch_arbitrage_candidates()
            print(f"✅ 发现 {len(markets)} 个活跃市场")

            if not markets:
                print("⚠️  未发现任何活跃市场")
                return False

            # 解析市场元数据并构建token映射
            print("\n🔍 正在解析市场数据...")
            for market in markets:
                try:
                    metadata = parse_market_metadata(market)
                    token_ids = metadata.get("token_ids", [])

                    if len(token_ids) >= 2:
                        # 二元市场: Yes和No
                        market_id = metadata.get("condition_id", "unknown")
                        question = metadata.get("question", "Unknown")

                        # 构建映射：token_id -> (market_id, side)
                        self.market_tokens[token_ids[0]] = {
                            "market_id": market_id,
                            "side": "Yes",
                            "question": question
                        }
                        self.market_tokens[token_ids[1]] = {
                            "market_id": market_id,
                            "side": "No",
                            "question": question
                        }

                        print(f"  • 市场: {question[:50]}...")
                        print(f"    Token IDs: {token_ids[0]}, {token_ids[1]}")

                except Exception as e:
                    print(f"⚠️  解析市场时出错: {e}")
                    continue

            print(f"\n✅ 成功准备 {len(self.market_tokens)} 个代币进行监控")
            return len(self.market_tokens) > 0

        except Exception as e:
            print(f"❌ 扫描市场失败: {e}")
            return False

    def start_monitoring(self):
        """启动订单簿监控"""
        if not self.market_tokens:
            print("⚠️  没有可监控的市场")
            return False

        try:
            print(f"\n📡 启动WebSocket监控...")
            print(f"   监控 {len(self.market_tokens)} 个代币")

            # 传递执行器函数到监控器
            self.monitor = OrderBookMonitor(
                market_tokens=self.market_tokens,
                threshold=Config.ARBITRAGE_THRESHOLD,
                executor_func=self.execute_arbitrage_opportunity
            )

            # 在独立线程中运行WebSocket
            self.running = True
            ws_thread = threading.Thread(target=self.monitor.start, daemon=True)
            ws_thread.start()

            print("✅ WebSocket监控已启动")
            return True

        except Exception as e:
            print(f"❌ 启动监控失败: {e}")
            return False

    def execute_arbitrage_opportunity(self, market_id: str, yes_price: float, no_price: float):
        """
        执行套利交易
        参数:
            market_id: 市场ID
            yes_price: Yes代币价格
            no_price: No代币价格
        """
        try:
            print(f"\n" + "!" * 60)
            print(f"🎯 检测到套利机会!")
            print(f"   市场ID: {market_id}")
            print(f"   Yes价格: {yes_price:.4f}")
            print(f"   No价格: {no_price:.4f}")
            print(f"   总成本: {yes_price + no_price:.4f}")
            print(f"   预期利润: {(1 - (yes_price + no_price)) * 100:.2f}%")
            print(f"!" * 60 + "\n")

            # 获取对应的token IDs
            token_yes = None
            token_no = None
            for token_id, info in self.market_tokens.items():
                if info["market_id"] == market_id:
                    if info["side"] == "Yes":
                        token_yes = token_id
                    elif info["side"] == "No":
                        token_no = token_id

            if token_yes and token_no:
                # 执行并发下单
                import asyncio
                asyncio.run(execute_arbitrage(
                    token_yes=token_yes,
                    token_no=token_no,
                    price_yes=yes_price,
                    price_no=no_price,
                    size=Config.DEFAULT_ORDER_SIZE
                ))
            else:
                print(f"⚠️  未找到对应的Token ID")

        except Exception as e:
            print(f"❌ 执行套利交易失败: {e}")

    def stop(self):
        """停止系统"""
        print("\n🛑 正在停止系统...")
        self.running = False

    def run(self):
        """运行系统主循环"""
        try:
            # 验证配置
            Config.validate()
            print("✅ 配置验证通过")

            # 扫描市场
            if not self.scan_markets():
                print("❌ 市场扫描失败，退出")
                return 1

            # 启动监控
            if not self.start_monitoring():
                print("❌ 监控启动失败，退出")
                return 1

            print("\n" + "=" * 60)
            print("✅ 系统运行中...")
            print("   按 Ctrl+C 退出")
            print("=" * 60 + "\n")

            # 保持主线程运行
            try:
                while self.running:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
                print("\n👋 系统已安全退出")
                return 0

        except Exception as e:
            print(f"\n❌ 系统运行错误: {e}")
            return 1

        return 0


def signal_handler(signum, frame):
    """信号处理器 - 优雅退出"""
    print("\n\n🛑 接收到退出信号...")
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 创建并运行系统
    system = ArbitrageSystem()
    return system.run()


if __name__ == "__main__":
    sys.exit(main())
