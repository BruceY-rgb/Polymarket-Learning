#!/usr/bin/env python3
"""
独立生成 markets.csv 文件
获取最近180天的市场数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_utils.update_markets import update_markets

def main():
    print("=" * 70)
    print("🏪 生成 Markets 数据")
    print("📊 获取最近 180 天的市场数据")
    print("=" * 70 + "\n")

    # 生成 markets.csv 文件
    # 输出到 /Users/yangsmac/Desktop/poly_data 目录
    update_markets(csv_filename="/Users/yangsmac/Desktop/poly_data/markets.csv", batch_size=500, days_limit=180)

    print("\n" + "=" * 70)
    print("✅ Markets 数据生成完成！")
    print("📁 输出文件: /Users/yangsmac/Desktop/poly_data/markets.csv")
    print("=" * 70)

if __name__ == "__main__":
    main()
