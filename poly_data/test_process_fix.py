#!/usr/bin/env python3
"""
测试 process_live 修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import subprocess

def test_process_fix():
    """测试 process_live 的修复"""
    print("🧪 测试 process_live 修复")
    print("=" * 40)

    # 检查数据文件
    print("\n📁 检查数据文件:")
    files = [
        'goldsky/orderFilled.csv',
        'markets.csv',
        'processed/trades.csv'
    ]

    for file_path in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path}: {size:,} 字节")
        else:
            print(f"  ❌ {file_path}: 不存在")

    # 检查 markets.csv 内容
    if os.path.exists('markets.csv'):
        print("\n📊 检查 markets.csv 内容:")
        try:
            with open('markets.csv', 'r') as f:
                lines = f.readlines()
                print(f"  总行数: {len(lines)}")
                if len(lines) > 1:
                    print("  有数据 ✅")
                    # 显示前几行
                    for i, line in enumerate(lines[:3]):
                        print(f"  行 {i+1}: {line.strip()}")
                else:
                    print("  仅有标题 ❌")
        except Exception as e:
            print(f"  读取错误: {e}")

    # 检查 orderFilled.csv 内容
    if os.path.exists('goldsky/orderFilled.csv'):
        print("\n📊 检查 orderFilled.csv 内容:")
        try:
            with open('goldsky/orderFilled.csv', 'r') as f:
                lines = f.readlines()
                print(f"  总行数: {len(lines)}")
                if len(lines) > 1:
                    print("  有数据 ✅")
        except Exception as e:
            print(f"  读取错误: {e}")

    print("\n" + "=" * 40)
    print("✅ 测试完成")

if __name__ == "__main__":
    test_process_fix()
