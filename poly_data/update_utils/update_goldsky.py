import os
import json
import pandas as pd
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from flatten_json import flatten
from datetime import datetime, timedelta, timezone
import subprocess
import time
from update_utils.update_markets import update_markets

# Global runtime timestamp - set once when program starts
RUNTIME_TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# 默认时间范围限制（设置为半年回溯）
DEFAULT_DAYS_LIMIT = 180  # 半年 = 180 天

# Columns to save
COLUMNS_TO_SAVE = ['timestamp', 'maker', 'makerAssetId', 'makerAmountFilled', 'taker', 'takerAssetId', 'takerAmountFilled', 'transactionHash']

# No need to create goldsky directory anymore - files go to root directory

CURSOR_FILE = '/Users/yangsmac/Desktop/poly_data/cursor_state.json'

def save_cursor(timestamp, last_id, sticky_timestamp=None):
    """Save cursor state to file for efficient resume."""
    state = {
        'last_timestamp': timestamp,
        'last_id': last_id,
        'sticky_timestamp': sticky_timestamp
    }
    with open(CURSOR_FILE, 'w') as f:
        json.dump(state, f)

def get_latest_cursor(days_limit: int = DEFAULT_DAYS_LIMIT):
    """获取最新的光标状态以高效恢复。
    返回 (timestamp, last_id, sticky_timestamp) 元组。
    新策略：从最新数据开始，向前回溯指定天数
    Args:
        days_limit: 时间范围限制（天数），默认向前回溯 180 天（半年）
    """
    # 计算时间范围
    # 使用更兼容的时区处理方式
    current_time = datetime.now(tz=timezone.utc)
    start_time = current_time - timedelta(days=days_limit)
    start_timestamp = int(start_time.timestamp())
    current_timestamp = int(current_time.timestamp())

    print(f"🔄 数据收集策略：从最新数据开始，向前回溯 {days_limit} 天")
    print(f"📅 起始时间（回溯起点）: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (timestamp: {start_timestamp})")
    print(f"📅 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (timestamp: {current_timestamp})")

    # Fallback: read from CSV file
    cache_file = '/Users/yangsmac/Desktop/poly_data/orderFilled.csv'

    # 检查是否已有数据文件
    if os.path.isfile(cache_file):
        try:
            # 获取文件中的最新时间戳
            result = subprocess.run(['tail', '-n', '1', cache_file], capture_output=True, text=True, check=True)
            last_line = result.stdout.strip()
            if last_line:
                # Get header to find column indices
                header_result = subprocess.run(['head', '-n', '1', cache_file], capture_output=True, text=True, check=True)
                headers = header_result.stdout.strip().split(',')

                if 'timestamp' in headers:
                    timestamp_index = headers.index('timestamp')
                    values = last_line.split(',')
                    if len(values) > timestamp_index:
                        file_last_timestamp = int(values[timestamp_index])

                        # 如果文件中的最新数据晚于我们的回溯起点，从最新开始
                        if file_last_timestamp > start_timestamp:
                            readable_time = datetime.fromtimestamp(file_last_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
                            print(f"✅ 发现较新数据：文件最新 timestamp {file_last_timestamp} ({readable_time})")
                            print(f"🔄 从最新数据开始回溯...")
                            # 从文件中的最新时间戳开始（减去1秒确保不重复）
                            return file_last_timestamp - 1, None, None
                        else:
                            print(f"⚠️ 文件数据较旧：最新 timestamp {file_last_timestamp} 早于回溯起点 {start_timestamp}")
                            print(f"🔄 重新从回溯起点开始...")
        except Exception as e:
            print(f"⚠️ 读取文件失败: {e}")

    # 如果没有现有数据或需要重新开始，从当前时间开始回溯
    print(f"🚀 初始运行：从当前时间开始回溯 {days_limit} 天")
    print(f"⏰ 起始点: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (timestamp: {current_timestamp})")
    return current_timestamp, None, None

def scrape(at_once=1000, days_limit: int = DEFAULT_DAYS_LIMIT):
    """从最新数据开始抓取订单成交事件，向前回溯指定天数"""
    QUERY_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/orderbook-subgraph/0.0.1/gn"
    print(f"GraphQL 端点: {QUERY_URL}")
    print(f"运行时间戳: {RUNTIME_TIMESTAMP}")

    # 计算回溯时间范围
    current_time = datetime.now(tz=timezone.utc)
    start_time = current_time - timedelta(days=days_limit)
    start_timestamp = int(start_time.timestamp())

    print(f"\n🔄 从最新数据开始，向前回溯 {days_limit} 天")
    print(f"📅 回溯起点: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (timestamp: {start_timestamp})")

    # Get starting cursor from latest file (includes sticky state for perfect resume)
    last_timestamp, last_id, sticky_timestamp = get_latest_cursor(days_limit)
    count = 0
    total_records = 0

    print(f"\n🚀 开始抓取 orderFilledEvents")
    print(f"📂 输出文件: /Users/yangsmac/Desktop/poly_data/orderFilled.csv")
    print(f"📋 保存列: {COLUMNS_TO_SAVE}")

    # 存储所有数据，最后统一排序
    all_data = []

    while True:
        # Build the where clause based on cursor state
        if sticky_timestamp is not None:
            # We're in sticky mode: stay at this timestamp and paginate by id
            where_clause = f'timestamp: "{sticky_timestamp}", id_lt: "{last_id}"'
        else:
            # 回溯模式：从当前时间戳向前查找到指定时间范围
            if last_timestamp is None:
                # 第一次：从当前时间开始
                where_clause = f'timestamp_lte: "{int(current_time.timestamp())}"'
            else:
                # 继续向前回溯
                where_clause = f'timestamp_lt: "{last_timestamp}", timestamp_gte: "{start_timestamp}"'

        q_string = f'''query MyQuery {{
                        orderFilledEvents(orderBy: timestamp, orderDirection: desc
                                             first: {at_once}
                                             where: {{{where_clause}}}) {{
                            fee
                            id
                            maker
                            makerAmountFilled
                            makerAssetId
                            orderHash
                            taker
                            takerAmountFilled
                            takerAssetId
                            timestamp
                            transactionHash
                        }}
                    }}'''

        query = gql(q_string)
        transport = RequestsHTTPTransport(url=QUERY_URL, verify=True, retries=3)
        client = Client(transport=transport)

        try:
            print(f"⏳ 获取批次 {count + 1}...")
            res = client.execute(query)
        except Exception as e:
            print(f"❌ 查询错误: {e}")
            print("🔄 5 秒后重试...")
            time.sleep(5)
            continue

        if not res['orderFilledEvents'] or len(res['orderFilledEvents']) == 0:
            if sticky_timestamp is not None:
                # Exhausted events at sticky timestamp, advance to next timestamp
                last_timestamp = sticky_timestamp
                sticky_timestamp = None
                last_id = None
                continue
            print(f"✅ 没有更多数据，停止抓取")
            break

        df = pd.DataFrame([flatten(x) for x in res['orderFilledEvents']]).reset_index(drop=True)

        # 检查是否到达回溯时间范围
        batch_first_timestamp = int(df.iloc[-1]['timestamp'])  # 注意：desc 排序，最后一行是最早的

        if batch_first_timestamp < start_timestamp:
            # 数据已经早于回溯范围，停止
            print(f"🛑 已到达回溯时间范围边界 (timestamp: {batch_first_timestamp} < {start_timestamp})")
            # 只保留在时间范围内的数据
            df = df[df['timestamp'].astype(int) >= start_timestamp]
            if len(df) > 0:
                all_data.append(df)
                total_records += len(df)
                print(f"📝 添加最后一批数据：{len(df)} 条记录")
            break

        # Sort by timestamp and id for consistent ordering
        df = df.sort_values(['timestamp', 'id'], ascending=True).reset_index(drop=True)

        batch_last_timestamp = int(df.iloc[-1]['timestamp'])
        batch_last_id = df.iloc[-1]['id']
        batch_first_timestamp = int(df.iloc[0]['timestamp'])

        readable_time = datetime.fromtimestamp(batch_first_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Determine if we need sticky cursor for next iteration
        if len(df) >= at_once:
            # Batch is full - check if all events are at the same timestamp
            if batch_first_timestamp == batch_last_timestamp:
                # All events at same timestamp, need to continue paginating at this timestamp
                sticky_timestamp = batch_first_timestamp
                last_id = batch_last_id
                print(f"批次 {count + 1}: 时间戳 {batch_first_timestamp} ({readable_time}), 记录数: {len(df)} [STICKY - 同时间戳继续]")
            else:
                # Mixed timestamps - we need to continue from the earliest timestamp in this batch
                sticky_timestamp = batch_first_timestamp
                last_id = batch_last_id
                print(f"批次 {count + 1}: 时间范围 {batch_first_timestamp}-{batch_last_timestamp} ({readable_time}), 记录数: {len(df)} [STICKY - 确保完整性]")
        else:
            # Batch not full - we have all events, can advance normally
            if sticky_timestamp is not None:
                # We were in sticky mode, now exhausted - advance past this timestamp
                last_timestamp = sticky_timestamp
                sticky_timestamp = None
                last_id = None
                print(f"批次 {count + 1}: 时间戳 {batch_first_timestamp} ({readable_time}), 记录数: {len(df)} [STICKY 完成]")
            else:
                # Normal backward traversal
                last_timestamp = batch_first_timestamp
                print(f"批次 {count + 1}: 最早时间戳 {batch_first_timestamp} ({readable_time}), 记录数: {len(df)}")

        count += 1
        all_data.append(df)

        # Fixed stop logic: only stop when we've truly reached the end
        # Check if we should stop based on time boundary
        if batch_first_timestamp < start_timestamp:
            # We've gone past the time range - this is already handled above
            # but keeping as safety check
            print("🛑 已到达时间范围边界，停止抓取")
            break
        elif len(df) < at_once and sticky_timestamp is None:
            # Batch not full AND not in sticky mode
            # This could mean we're at the end OR just reached a sparse period
            # We need to check if we've truly exhausted all data
            print(f"⚠️ 批次不满({len(df)}/{at_once})，检查是否到达边界...")
            # Continue to next iteration to see if we get more data
            # If next iteration returns empty, then we know we're at the end

    # 合并所有数据并排序
    if all_data:
        print(f"\n📊 合并数据...")
        combined_df = pd.concat(all_data, ignore_index=True)
        # Remove duplicates (by id to be safe)
        combined_df = combined_df.drop_duplicates(subset=['id'])
        # 最终按时间戳升序排序
        combined_df = combined_df.sort_values('timestamp', ascending=True).reset_index(drop=True)

        output_file = '/Users/yangsmac/Desktop/poly_data/orderFilled.csv'

        # 保存数据
        if os.path.isfile(output_file):
            # 如果文件存在，先读取现有数据，去重后合并
            existing_df = pd.read_csv(output_file)
            if len(existing_df) > 0:
                # 合并并去重
                final_df = pd.concat([existing_df, combined_df]).drop_duplicates(subset=['id'])
                final_df = final_df.sort_values('timestamp', ascending=True).reset_index(drop=True)
            else:
                final_df = combined_df

            final_df.to_csv(output_file, index=None)
            total_records = len(final_df)
            print(f"✅ 更新文件：{output_file}")
        else:
            combined_df.to_csv(output_file, index=None)
            total_records = len(combined_df)
            print(f"✅ 创建文件：{output_file}")

        print(f"📈 总记录数：{total_records:,}")
    else:
        print("⚠️ 没有获取到任何数据")

    # Clear cursor file on successful completion
    if os.path.isfile(CURSOR_FILE):
        os.remove(CURSOR_FILE)

    print(f"\n🎉 抓取完成！")
    print(f"📊 总新记录数: {total_records}")
    print(f"📁 输出文件: /Users/yangsmac/Desktop/poly_data/orderFilled.csv")

def update_goldsky(days_limit: int = DEFAULT_DAYS_LIMIT):
    """运行订单成交事件抓取 - 从最新数据开始，向前回溯指定天数

    Args:
        days_limit: 回溯天数，默认 180 天（半年）
    """
    print(f"\n{'='*60}")
    print(f"🚀 开始抓取 orderFilledEvents")
    print(f"⏰ 运行时间: {RUNTIME_TIMESTAMP}")
    print(f"📅 回溯范围: 最近 {days_limit} 天")
    print(f"{'='*60}")
    try:
        scrape(days_limit=days_limit)
        print(f"\n✅ orderFilledEvents 抓取完成")
    except Exception as e:
        print(f"\n❌ orderFilledEvents 抓取错误: {str(e)}")