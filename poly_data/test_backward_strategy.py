#!/usr/bin/env python3
"""
测试半年回溯策略的脚本
验证新版本是否从最新数据开始回溯
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone, timedelta
from update_utils.update_goldsky import get_latest_cursor, DEFAULT_DAYS_LIMIT

def test_backward_strategy():
    """测试新的回溯策略"""
    print("="*70)
    print("🧪 测试半年回溯策略")
    print("="*70)

    # 显示当前配置
    print(f"\n📋 当前配置:")
    print(f"  默认回溯天数: {DEFAULT_DAYS_LIMIT}")

    # 计算预期时间范围
    current_time = datetime.now(tz=timezone.utc)
    start_time = current_time - timedelta(days=DEFAULT_DAYS_LIMIT)

    print(f"\n📅 预期时间范围:")
    print(f"  当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  回溯起点: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  回溯天数: {DEFAULT_DAYS_LIMIT}")

    # 测试光标获取逻辑
    print(f"\n🔍 测试光标获取逻辑:")

    try:
        timestamp, last_id, sticky_timestamp = get_latest_cursor(DEFAULT_DAYS_LIMIT)

        print(f"  ✅ 光标获取成功!")
        print(f"  📍 返回值:")
        print(f"    - timestamp: {timestamp}")
        print(f"    - last_id: {last_id}")
        print(f"    - sticky_timestamp: {sticky_timestamp}")

        # 验证时间戳是否合理
        if timestamp > 0:
            readable_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            print(f"  🕐 时间戳解析: {readable_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

            # 检查是否在未来（不应该）
            if timestamp > int(current_time.timestamp()):
                print(f"  ⚠️  警告: 时间戳在未来")
            else:
                print(f"  ✅ 时间戳合理（在当前或过去）")

    except Exception as e:
        print(f"  ❌ 光标获取失败: {e}")
        return False

    # 检查数据文件
    print(f"\n📁 检查数据文件:")
    data_file = 'goldsky/orderFilled.csv'

    if os.path.exists(data_file):
        size = os.path.getsize(data_file)
        print(f"  ✅ 文件存在: {data_file}")
        print(f"  📊 文件大小: {size:,} 字节")

        if size > 0:
            print(f"  💡 文件有数据，可以测试增量更新")
        else:
            print(f"  💡 文件为空，将执行初始回溯")
    else:
        print(f"  📝 文件不存在: {data_file}")
        print(f"  💡 将执行初始回溯")

    # 显示 GraphQL 查询示例
    print(f"\n🔍 GraphQL 查询示例:")
    print(f"  端点: https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn")
    print(f"  排序: timestamp (desc - 从新到旧)")
    print(f"  过滤: timestamp >= {int(start_time.timestamp())}")
    print(f"  批次大小: 1000")

    print(f"\n" + "="*70)
    print(f"✅ 测试完成！")
    print(f"="*70)

    print(f"\n🚀 下一步操作:")
    print(f"1. 运行完整测试: uv run python test_apis.py")
    print(f"2. 开始数据收集: uv run python -c \"from update_utils.update_goldsky import update_goldsky; update_goldsky()\"")
    print(f"3. 或运行完整管道: uv run python update_all.py")

    return True

def test_custom_days(days):
    """测试自定义天数"""
    print(f"\n" + "="*70)
    print(f"🧪 测试自定义回溯策略: {days} 天")
    print(f"="*70)

    current_time = datetime.now(tz=timezone.utc)
    start_time = current_time - timedelta(days=days)

    print(f"\n📅 时间范围:")
    print(f"  当前: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"  回溯起点: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    try:
        timestamp, last_id, sticky_timestamp = get_latest_cursor(days)
        print(f"\n✅ 自定义天数测试成功!")

        if timestamp > 0:
            readable_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            print(f"  📍 光标时间: {readable_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

    return True

def main():
    print("\n🎯 Polymarket 数据收集策略测试工具")
    print("="*70)

    # 运行默认测试
    test_backward_strategy()

    # 询问是否测试自定义天数
    print(f"\n" + "="*70)
    response = input("🤔 是否测试自定义天数? (y/N): ").strip().lower()

    if response in ['y', 'yes', '是']:
        try:
            days = int(input("请输入回溯天数 (例如 30, 90, 365): ").strip())
            if 1 <= days <= 10000:
                test_custom_days(days)
            else:
                print("❌ 天数应在 1-10000 之间")
        except ValueError:
            print("❌ 请输入有效数字")

    print(f"\n🎉 测试结束！")

if __name__ == "__main__":
    main()
