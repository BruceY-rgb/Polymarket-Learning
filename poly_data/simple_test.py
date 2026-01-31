#!/usr/bin/env python3
"""
简单测试 API 和时间解析
"""

import requests
from datetime import datetime, timezone, timedelta
import re

def simple_test():
    print("🔍 简单 API 和时间测试")
    print("=" * 40)

    # 计算半年时间戳
    current_time = datetime.now(tz=timezone.utc)
    six_months_ago = current_time - timedelta(days=180)
    start_timestamp = int(six_months_ago.timestamp())

    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"半年时间: {six_months_ago.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"起始时间戳: {start_timestamp}")
    print()

    # 调用 API
    base_url = "https://gamma-api.polymarket.com/markets"
    params = {
        'order': 'createdAt',
        'ascending': 'true',
        'limit': 5
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"API 状态: {response.status_code}")

        if response.status_code == 200:
            markets = response.json()
            print(f"获取市场数: {len(markets)}")
            print()

            for i, market in enumerate(markets):
                print(f"市场 {i+1}:")
                print(f"  ID: {market.get('id')}")
                print(f"  创建时间: {market.get('createdAt')}")

                # 解析时间
                created_at = market.get('createdAt', '')
                try:
                    if isinstance(created_at, str) and 'T' in created_at:
                        match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', created_at)
                        if match:
                            time_str = match.group(1).replace('T', ' ') + ' +00:00'
                            dt = datetime.fromisoformat(time_str)
                            created_timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())
                            readable = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

                            print(f"  解析时间: {readable}")
                            print(f"  时间戳: {created_timestamp}")

                            if created_timestamp >= start_timestamp:
                                print(f"  ✅ 在范围内")
                            else:
                                print(f"  ❌ 早于范围 (起始: {start_timestamp})")
                    else:
                        print(f"  ⚠️ 无法解析格式")
                except Exception as e:
                    print(f"  ❌ 解析错误: {e}")
                print()

        else:
            print(f"API 错误: {response.status_code}")

    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    simple_test()
