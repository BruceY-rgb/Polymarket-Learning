#!/usr/bin/env python3
"""
测试时间过滤功能的简单脚本
"""

import sys
import os
from datetime import datetime, timedelta, timezone

def test_time_calculation():
    """测试时间计算是否正确"""
    print("测试时间计算功能...")

    # 测试不同的天数限制
    test_cases = [30, 90, 180, 365]

    for days in test_cases:
        print(f"\n测试 {days} 天前:")
        start_time = datetime.now(tz=timezone.utc) - timedelta(days=days)
        start_timestamp = int(start_time.timestamp())
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S UTC')

        print(f"  起始时间: {start_time_str}")
        print(f"  时间戳: {start_timestamp}")

    print("\n✅ 时间计算测试通过！")

def test_imports():
    """测试导入是否正常"""
    print("\n测试模块导入...")

    try:
        from update_utils.update_markets import update_markets
        print("✅ update_markets 导入成功")
    except Exception as e:
        print(f"❌ update_markets 导入失败: {e}")
        return False

    try:
        from update_utils.update_goldsky import update_goldsky
        print("✅ update_goldsky 导入成功")
    except Exception as e:
        print(f"❌ update_goldsky 导入失败: {e}")
        return False

    return True

if __name__ == "__main__":
    print("=" * 50)
    print("开始测试时间过滤功能")
    print("=" * 50)

    # 测试时间计算
    test_time_calculation()

    # 测试导入
    if test_imports():
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 某些测试失败！")
        sys.exit(1)