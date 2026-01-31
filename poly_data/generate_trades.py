#!/usr/bin/env python3
"""
独立生成 trades.csv 文件
基于 orderFilled.csv 生成处理后的交易数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_utils.process_live import process_live

def main():
    print("=" * 70)
    print("🔄 生成 Trades 数据")
    print("📊 基于 orderFilled.csv 生成处理后的交易数据")
    print("=" * 70 + "\n")

    # 检查 orderFilled.csv 是否存在
    if not os.path.exists("/Users/yangsmac/Desktop/poly_data/orderFilled.csv"):
        print("❌ 错误：找不到 /Users/yangsmac/Desktop/poly_data/orderFilled.csv 文件")
        print("请先运行 generate_orders.py 生成订单数据")
        sys.exit(1)

    print("✓ 找到 /Users/yangsmac/Desktop/poly_data/orderFilled.csv 文件")
    print()

    # 生成 trades.csv 文件
    # 输入: /Users/yangsmac/Desktop/poly_data/orderFilled.csv
    # 输出: /Users/yangsmac/Desktop/poly_data/trades.csv
    process_live()

    print("\n" + "=" * 70)
    print("✅ Trades 数据生成完成！")
    print("📁 输出文件: /Users/yangsmac/Desktop/poly_data/trades.csv")
    print("=" * 70)

if __name__ == "__main__":
    main()
