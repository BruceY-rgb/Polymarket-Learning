#!/usr/bin/env python3
"""
测试市场数据更新修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from datetime import datetime, timezone, timedelta

def test_api_call():
    """测试基本的 API 调用"""
    print("🔍 测试基本 API 调用...")

    base_url = "https://gamma-api.polymarket.com/markets"
    params = {
        'order': 'createdAt',
        'ascending': 'true',
        'limit': 3
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        print(f"HTTP 状态码: {response.status_code}")

        if response.status_code == 200:
            markets = response.json()
            print(f"✅ API 返回 {len(markets)} 个市场")

            # 测试时间解析
            start_timestamp = int((datetime.now(tz=timezone.utc) - timedelta(days=180)).timestamp())

            for i, market in enumerate(markets):
                created_at = market.get('createdAt', '')
                print(f"\n市场 {i+1}:")
                print(f"  ID: {market.get('id')}")
                print(f"  创建时间: {created_at}")

                # 解析时间
                try:
                    if isinstance(created_at, str) and 'T' in created_at:
                        # ISO 格式
                        from datetime import datetime
                        import re
                        match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', created_at)
                        if match:
                            time_str = match.group(1).replace('T', ' ') + ' +00:00'
                            dt = datetime.fromisoformat(time_str)
                            created_timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())
                            readable = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                            print(f"  解析后时间: {readable} (timestamp: {created_timestamp})")

                            if created_timestamp >= start_timestamp:
                                print(f"  ✅ 在时间范围内")
                            else:
                                print(f"  ❌ 早于时间范围")
                        else:
                            print(f"  ⚠️ 无法解析时间格式")
                    else:
                        print(f"  ⚠️ 未知时间格式")
                except Exception as e:
                    print(f"  ❌ 时间解析错误: {e}")

            return True
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_with_time_filter():
    """测试带时间过滤的调用"""
    print("\n🔍 测试带时间过滤的 API 调用...")

    from datetime import datetime, timezone, timedelta

    base_url = "https://gamma-api.polymarket.com/markets"
    start_timestamp = int((datetime.now(tz=timezone.utc) - timedelta(days=180)).timestamp())

    params = {
        'order': 'createdAt',
        'ascending': 'true',
        'limit': 5,
        'offset': 0
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)

        if response.status_code == 200:
            markets = response.json()
            print(f"✅ 获取到 {len(markets)} 个市场")

            # 本地过滤
            valid_markets = []
            for market in markets:
                created_at = market.get('createdAt', '')
                try:
                    if isinstance(created_at, str) and 'T' in created_at:
                        import re
                        match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', created_at)
                        if match:
                            time_str = match.group(1).replace('T', ' ') + ' +00:00'
                            dt = datetime.fromisoformat(time_str)
                            created_timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())

                            if created_timestamp >= start_timestamp:
                                valid_markets.append(market)
                    else:
                        # 其他格式，假设有效
                        valid_markets.append(market)
                except Exception as e:
                    print(f"跳过市场 {market.get('id')}: {e}")

            print(f"✅ 过滤后有效市场: {len(valid_markets)}")
            return len(valid_markets) > 0
        else:
            print(f"❌ API 调用失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 市场数据更新修复测试")
    print("=" * 50)

    # 基本 API 测试
    basic_ok = test_api_call()

    # 时间过滤测试
    filter_ok = test_with_time_filter()

    print("\n" + "=" * 50)
    print("📋 测试结果:")
    print(f"  基本 API 调用: {'✅ 正常' if basic_ok else '❌ 异常'}")
    print(f"  时间过滤测试: {'✅ 正常' if filter_ok else '❌ 异常'}")

    if basic_ok and filter_ok:
        print("\n🎉 修复验证成功！可以运行完整管道")
    else:
        print("\n⚠️ 存在问题，需要进一步调试")
