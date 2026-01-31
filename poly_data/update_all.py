from update_utils.update_markets import update_markets
from update_utils.update_goldsky import update_goldsky
from update_utils.process_live import process_live

# 默认时间范围限制（半年 = 180 天）
DEFAULT_DAYS_LIMIT = 180

if __name__ == "__main__":
    # 获取命令行参数中的天数限制（可选）
    import sys
    days_limit = DEFAULT_DAYS_LIMIT
    if len(sys.argv) > 1:
        try:
            days_limit = int(sys.argv[1])
            print(f"使用命令行参数: {days_limit} 天")
        except ValueError:
            print(f"无效的参数，使用默认值: {DEFAULT_DAYS_LIMIT} 天")

    print("\n" + "=" * 70)
    print("🚀 Polymarket 数据收集管道")
    print("📊 新策略：从最新数据开始，向前回溯指定天数")
    print(f"⏰ 时间范围: 最近 {days_limit} 天")
    print("=" * 70 + "\n")

    print("📊 步骤 1/3: 更新市场数据")
    update_markets(days_limit=days_limit)

    print("\n📊 步骤 2/3: 更新 Goldsky 订单数据")
    update_goldsky(days_limit=days_limit)

    print("\n📊 步骤 3/3: 处理实时交易数据")
    process_live()

    print("\n" + "=" * 70)
    print("✅ 数据收集完成！")
    print("📁 数据文件：")
    print("  - markets.csv: 市场元数据")
    print(f"  - goldsky/orderFilled.csv: 最近 {days_limit} 天的订单数据")
    print("  - processed/trades.csv: 处理后交易数据")
    print("\n💡 提示：运行 'uv run jupyter notebook' 开始分析")
    print("=" * 70)