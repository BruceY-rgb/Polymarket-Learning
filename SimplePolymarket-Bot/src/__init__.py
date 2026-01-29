"""
Polymarket套利交易系统

该系统用于检测和执行Polymarket上的套利交易机会。
"""

__version__ = "1.0.0"
__author__ = "Polymarket Trader"

# 导出主要类
from .config import Config
from .Scanner import fetch_arbitrage_candidates, parse_market_metadata
from .Monitor import OrderBookMonitor
from .Executor import place_order_safe, execute_arbitrage
from .Settler import merge_position_on_chain

__all__ = [
    "Config",
    "fetch_arbitrage_candidates",
    "parse_market_metadata",
    "OrderBookMonitor",
    "place_order_safe",
    "execute_arbitrage",
    "merge_position_on_chain",
]
