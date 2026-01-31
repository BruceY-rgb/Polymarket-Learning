#!/usr/bin/env python3
"""
API 连接诊断脚本
用于测试 Polymarket API 和 Goldsky GraphQL API 的可用性
"""

import requests
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timezone
import time

def test_polymarket_api():
    """测试 Polymarket API"""
    print("\n" + "="*60)
    print("🔍 测试 Polymarket API")
    print("="*60)

    url = "https://gamma-api.polymarket.com/markets"
    params = {
        'order': 'createdAt',
        'ascending': 'true',
        'limit': 5  # 只获取 5 条记录进行测试
    }

    try:
        print(f"🌐 请求 URL: {url}")
        print(f"📋 请求参数: {params}")
        response = requests.get(url, params=params, timeout=30)
        print(f"📊 HTTP 状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 调用成功！获取到 {len(data)} 条记录")

            if data:
                print("\n📄 示例数据:")
                print(f"  - 第一条记录 ID: {data[0].get('id', 'N/A')}")
                print(f"  - 创建时间: {data[0].get('createdAt', 'N/A')}")
                print(f"  - 问题: {data[0].get('question', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ API 调用失败")
            print(f"   响应内容: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_goldsky_api():
    """测试 Goldsky GraphQL API"""
    print("\n" + "="*60)
    print("🔍 测试 Goldsky GraphQL API")
    print("="*60)

    QUERY_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn"

    # 计算时间戳（最近 30 天）
    start_time = datetime.now(tz=timezone.utc).timestamp() - (30 * 24 * 60 * 60)
    start_timestamp = int(start_time)

    q_string = f'''query MyQuery {{
        orderFilledEvents(
            orderBy: timestamp
            orderDirection: asc
            first: 5
            where: {{
                timestamp_gt: "{start_timestamp}"
            }}
        ) {{
            id
            timestamp
            maker
            makerAmountFilled
        }}
    }}'''

    try:
        print(f"🌐 GraphQL 端点: {QUERY_URL}")
        print(f"📅 时间范围: 最近 30 天 (timestamp >= {start_timestamp})")

        query = gql(q_string)
        transport = RequestsHTTPTransport(url=QUERY_URL, verify=True, retries=3)
        client = Client(transport=transport)

        print("⏳ 发送 GraphQL 查询...")
        res = client.execute(query)

        if 'orderFilledEvents' in res:
            events = res['orderFilledEvents']
            print(f"✅ GraphQL 查询成功！获取到 {len(events)} 条记录")

            if events:
                print("\n📄 示例数据:")
                print(f"  - 第一条记录 ID: {events[0].get('id', 'N/A')}")
                print(f"  - 时间戳: {events[0].get('timestamp', 'N/A')}")
                print(f"  - 发起者: {events[0].get('maker', 'N/A')[:20]}...")
            return True
        else:
            print("❌ GraphQL 响应格式异常")
            return False
    except Exception as e:
        print(f"❌ GraphQL 查询异常: {e}")
        return False

def check_data_files():
    """检查数据文件状态"""
    print("\n" + "="*60)
    print("📁 检查数据文件")
    print("="*60)

    import os

    files_to_check = [
        'markets.csv',
        'goldsky/orderFilled.csv',
        'processed/trades.csv'
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {size} 字节")
        else:
            print(f"❌ {file_path}: 文件不存在")

def main():
    print("\n" + "🚀 Polymarket API 诊断工具")
    print("="*60)
    print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # 检查数据文件
    check_data_files()

    # 测试 Polymarket API
    polymarket_ok = test_polymarket_api()

    # 测试 Goldsky API
    goldsky_ok = test_goldsky_api()

    # 总结
    print("\n" + "="*60)
    print("📋 诊断总结")
    print("="*60)
    print(f"Polymarket API: {'✅ 正常' if polymarket_ok else '❌ 异常'}")
    print(f"Goldsky API:    {'✅ 正常' if goldsky_ok else '❌ 异常'}")

    if polymarket_ok and goldsky_ok:
        print("\n🎉 所有 API 正常！可以运行完整的数据收集流程:")
        print("   uv run python update_all.py")
    else:
        print("\n⚠️  部分 API 异常，请检查网络连接或 API 状态")

if __name__ == "__main__":
    main()
