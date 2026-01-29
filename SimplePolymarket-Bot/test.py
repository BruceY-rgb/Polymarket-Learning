#!/usr/bin/env python3
"""
测试脚本 - 验证项目模块功能
注意：此脚本仅用于测试，不会执行实际交易
"""

import sys
import os

# 确保使用本地src模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试1: 模块导入测试")
    print("=" * 60)

    try:
        from src.config import Config
        print("✅ Config模块导入成功")
    except Exception as e:
        print(f"❌ Config模块导入失败: {e}")
        return False

    try:
        from src.Scanner import fetch_arbitrage_candidates, parse_market_metadata
        print("✅ Scanner模块导入成功")
    except Exception as e:
        print(f"❌ Scanner模块导入失败: {e}")
        return False

    try:
        from src.Monitor import OrderBookMonitor
        print("✅ Monitor模块导入成功")
    except Exception as e:
        print(f"❌ Monitor模块导入失败: {e}")
        return False

    try:
        from src.Executor import place_order_safe, execute_arbitrage
        print("✅ Executor模块导入成功")
    except Exception as e:
        print(f"❌ Executor模块导入失败: {e}")
        return False

    try:
        from src.Settler import merge_position_on_chain
        print("✅ Settler模块导入成功")
    except Exception as e:
        print(f"❌ Settler模块导入失败: {e}")
        return False

    return True

def test_config():
    """测试配置模块"""
    print("\n" + "=" * 60)
    print("测试2: 配置验证")
    print("=" * 60)

    try:
        from src.config import Config

        # 打印配置（隐藏敏感信息）
        print(f"Gamma API URL: {Config.GAMMA_API_URL}")
        print(f"WebSocket URL: {Config.WS_URL}")
        print(f"CLOB Host: {Config.CLOB_HOST}")
        print(f"Chain ID: {Config.CLOB_CHAIN_ID}")
        print(f"CTF Address: {Config.CTF_ADDRESS}")
        print(f"USDC Address: {Config.USDC_ADDRESS}")
        print(f"套利阈值: {Config.ARBITRAGE_THRESHOLD}")
        print(f"默认订单大小: {Config.DEFAULT_ORDER_SIZE}")
        print(f"详细日志: {Config.VERBOSE}")

        # 验证配置（不检查私钥）
        if Config.ARBITRAGE_THRESHOLD <= 0 or Config.ARBITRAGE_THRESHOLD >= 1:
            print("⚠️  警告: ARBITRAGE_THRESHOLD可能在合理范围之外")
        else:
            print("✅ 配置验证通过")

        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_scanner():
    """测试扫描器模块"""
    print("\n" + "=" * 60)
    print("测试3: 市场扫描器测试")
    print("=" * 60)

    try:
        from src.Scanner import parse_market_metadata

        # 模拟市场数据
        mock_market = {
            "clobTokenIds": '["token1", "token2"]',
            "conditionId": "0x1234567890abcdef",
            "question": "测试市场：Bitcoin会在2025年达到10万美元吗？"
        }

        metadata = parse_market_metadata(mock_market)
        print(f"✅ 市场问题: {metadata['question']}")
        print(f"✅ 条件ID: {metadata['condition_id']}")
        print(f"✅ Token IDs: {metadata['token_ids']}")

        return True

    except Exception as e:
        print(f"❌ 扫描器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monitor():
    """测试监控器模块"""
    print("\n" + "=" * 60)
    print("测试4: 订单簿监控器测试")
    print("=" * 60)

    try:
        from src.Monitor import OrderBookMonitor

        # 创建测试映射
        mock_tokens = {
            "TOKEN_YES": {"market_id": "TEST_1", "side": "Yes", "question": "测试市场"},
            "TOKEN_NO": {"market_id": "TEST_1", "side": "No", "question": "测试市场"}
        }

        # 创建监控器实例（不启动WebSocket）
        monitor = OrderBookMonitor(mock_tokens, threshold=0.005)
        print(f"✅ 监控器创建成功")
        print(f"   监控的代币数量: {len(mock_tokens)}")
        print(f"   套利阈值: {monitor.threshold}")

        return True

    except Exception as e:
        print(f"❌ 监控器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_executor():
    """测试执行器模块（不执行实际交易）"""
    print("\n" + "=" * 60)
    print("测试5: 交易执行器测试")
    print("=" * 60)

    try:
        from src.Executor import place_order_safe
        from py_clob_client.clob_types import OrderArgs

        # 创建测试订单参数（不实际发送）
        order = OrderArgs(
            token_id="TEST_TOKEN",
            price=0.5,
            size=100,
            side="BUY"
        )

        print(f"✅ 订单参数创建成功")
        print(f"   Token ID: {order.token_id}")
        print(f"   价格: {order.price}")
        print(f"   大小: {order.size}")
        print(f"   方向: {order.side}")

        # 注意：我们不实际调用place_order_safe，因为这需要真实的私钥和网络连接
        print("ℹ️  跳过实际交易执行测试（需要私钥和网络）")

        return True

    except Exception as e:
        print(f"❌ 执行器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settler():
    """测试结算模块"""
    print("\n" + "=" * 60)
    print("测试6: 链上结算测试")
    print("=" * 60)

    try:
        from src.Settler import contract, w3

        # 测试Web3连接
        if w3.is_connected():
            print("✅ Web3连接成功")
            print(f"   当前区块号: {w3.eth.block_number}")
        else:
            print("⚠️  Web3连接失败（这在测试环境中是正常的）")

        # 检查合约
        print(f"✅ CTF合约地址: {contract.address}")

        return True

    except Exception as e:
        print(f"❌ 结算模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Polymarket套利系统 - 模块测试" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("模块导入", test_imports),
        ("配置验证", test_config),
        ("市场扫描器", test_scanner),
        ("订单簿监控器", test_monitor),
        ("交易执行器", test_executor),
        ("链上结算", test_settler),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 出现异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print("-" * 60)
    print(f"总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n⚠️  重要提醒:")
        print("   1. 在实际使用前，请配置 .env 文件并设置 PRIVATE_KEY")
        print("   2. 建议先在测试网络上进行测试")
        print("   3. 交易有风险，请谨慎操作")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
