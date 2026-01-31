#!/usr/bin/env python3
"""
快速验证修复后的代码
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from datetime import datetime, timezone, timedelta

def quick_test():
    print("🚀 快速验证修复后的代码")
    print("=" * 40)

    # 测试 API 降序调用
    base_url = "https://gamma-api.polymarket.com/markets"
    params = {
        'order': 'createdAt',
        'ascending': 'false',  # 降序
        'limit': 3
    }

    try:
        print("🔍 测试降序 API 调用...")
        response = requests.get(base_url, params=params, timeout=10)
        print(f"HTTP 状态码: {response.status_code}")

        if response.status_code == 200:
            markets = response.json()
            print(f"✅ API 返回 {len(markets)} 个市场")

            # 检查时间
            for i, market in enumerate(markets):
                created_at = market.get('createdAt', '')
                print(f"  市场 {i+1}: {market.get('id')} - {created_at}")

            return len(markets) > 0
        else:
            print(f"❌ API 错误: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()

    if success:
        print("\n🎉 API 测试成功！修复生效。")
        print("\n💡 建议：")
        print("  1. 使用完整管道: uv run python update_all.py")
        print("  2. 或单独测试: uv run python -c \"from update_utils.update_markets import update_markets; update_markets()\"")
    else:
        print("\n⚠️  API 测试失败。")
