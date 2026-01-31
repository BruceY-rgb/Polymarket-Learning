#!/usr/bin/env python3
"""
独立生成 orderFilled.csv 文件
获取最近180天的订单成交数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_utils.update_goldsky import update_goldsky

def main():
    print("=" * 70)
    print("📋 生成 OrderFilled 数据")
    print("📊 获取最近 180 天的订单成交数据")
    print("=" * 70 + "\n")

    # 生成 orderFilled.csv 文件
    # 输出到 /Users/yangsmac/Desktop/poly_data 目录
    update_goldsky(days_limit=180)

    print("\n" + "=" * 70)
    print("✅ OrderFilled 数据生成完成！")
    print("📁 输出文件: /Users/yangsmac/Desktop/poly_data/orderFilled.csv")
    print("=" * 70)

if __name__ == "__main__":
    main()
