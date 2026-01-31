import requests
import csv
import json
import os
from typing import List, Dict
from datetime import datetime, timedelta, timezone

def count_csv_lines(csv_filename: str) -> int:
    """计算 CSV 中数据行的数量（不包括标题）"""
    if not os.path.exists(csv_filename):
        return 0

    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # 跳过标题
            return sum(1 for row in reader if row)  # 计算非空行数
    except Exception as e:
        print(f"读取 CSV 错误：{e}")
        return 0

def update_markets(csv_filename: str = "/Users/yangsmac/Desktop/poly_data/markets.csv", batch_size: int = 500, days_limit: int = 180):
    """
    按创建日期获取市场并保存到 CSV。
    根据现有 CSV 行自动从正确的偏移恢复。
    默认获取最近 180 天的市场数据（与订单数据保持一致）。

    Args:
        csv_filename: 要保存的 CSV 文件名
        batch_size: 每次请求获取的市场数量
        days_limit: 时间范围限制（天数），默认 180 天
    """
    # 计算起始时间戳（半年=180天前）
    # 使用更兼容的时区处理方式
    six_months_ago = datetime.now(tz=timezone.utc) - timedelta(days=days_limit)
    start_timestamp = int(six_months_ago.timestamp())
    start_time_str = six_months_ago.strftime('%Y-%m-%d %H:%M:%S UTC')

    print(f"时间范围限制: 最近 {days_limit} 天")
    print(f"起始时间: {start_time_str} (timestamp: {start_timestamp})")

    base_url = "https://gamma-api.polymarket.com/markets"

    # 所需列的 CSV 标题
    headers = [
        'createdAt', 'id', 'question', 'answer1', 'answer2', 'neg_risk',
        'market_slug', 'token1', 'token2', 'condition_id', 'volume', 'ticker', 'closedTime'
    ]

    # 根据现有记录动态设置偏移
    current_offset = count_csv_lines(csv_filename)
    file_exists = os.path.exists(csv_filename) and current_offset > 0

    # 在使用时间过滤(createdAt_min)时，直接使用已有的 offset 可能会跳过过滤结果。
    # 如果现有 CSV 包含比当前 start_timestamp 更早的记录（即我们缩小了时间窗口），
    # 则更安全的做法是重建（覆盖）CSV 并从偏移 0 开始抓取与过滤条件一致的数据。
    mode = 'w'
    if file_exists:
        try:
            # 尝试读取 CSV 的第一条数据行（假定文件按 createdAt 升序存放，第一条为最早）
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                first_row = next(reader, None)

            if first_row and len(first_row) > 0:
                existing_created = str(first_row[0])
                existing_ts = None
                # 解析已有记录的 createdAt（支持数字时间戳或 ISO 格式）
                if existing_created.isdigit():
                    existing_ts = int(existing_created)
                    if existing_ts > 10**12:
                        existing_ts = existing_ts // 1000
                else:
                    try:
                        existing_dt = datetime.fromisoformat(existing_created.replace('Z', '+00:00'))
                        existing_ts = int(existing_dt.replace(tzinfo=timezone.utc).timestamp())
                    except Exception:
                        existing_ts = None

                if existing_ts is None:
                    print(f"无法解析现有 CSV 的创建时间 ({existing_created})，将重建 CSV 文件")
                    current_offset = 0
                    mode = 'w'
                else:
                    # 如果已有最早记录早于当前起始时间，则现有 offset 与过滤后的 API 结果不匹配
                    if existing_ts < start_timestamp:
                        print(f"现有 CSV 包含早于起始时间的记录 ({existing_created})，将重建 CSV 以匹配新的时间范围")
                        current_offset = 0
                        mode = 'w'
                    else:
                        print(f"找到 {current_offset} 个现有记录。从偏移 {current_offset} 恢复")
                        mode = 'a'
            else:
                print(f"无法读取现有 CSV 的第一条记录，重新创建文件：{csv_filename}")
                current_offset = 0
                mode = 'w'
        except Exception as e:
            print(f"读取现有 CSV 失败：{e}，将重建 CSV 文件")
            current_offset = 0
            mode = 'w'

    total_fetched = 0
    
    with open(csv_filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 仅在新文件时写入标题
        if mode == 'w':
            writer.writerow(headers)

        count = 0

        while True:
            print(f"第{count + 1}批次：在偏移 {current_offset} 处获取批次...")

            count += 1

            try:
                params = {
                    'order': 'createdAt',
                    'ascending': 'false',  # 改为降序，获取最新市场
                    'limit': batch_size,
                    'offset': current_offset
                    # 移除不被支持的 createdAt_min 参数，改用本地过滤
                }

                response = requests.get(base_url, params=params, timeout=30)

                # 处理不同的 HTTP 状态码
                if response.status_code == 500:
                    print(f"服务器错误 (500) - 5 秒后重试...")
                    import time
                    time.sleep(5)
                    continue
                elif response.status_code == 429:
                    print(f"达到速率限制 (429) - 等待 10 秒...")
                    import time
                    time.sleep(10)
                    continue
                elif response.status_code != 200:
                    print(f"API 错误 {response.status_code}：{response.text}")
                    print("3 秒后重试...")
                    import time
                    time.sleep(3)
                    continue

                markets = response.json()

                if not markets:
                    print(f"在偏移 {current_offset} 处未找到更多市场。完成！")
                    break
                
                batch_count = 0
                
                for market in markets:
                    try:
                        # 检查市场创建时间是否在半年内
                        created_at = market.get('createdAt', '')
                        if created_at:
                            try:
                                # 尝试解析时间戳（可能是毫秒）
                                if isinstance(created_at, str) and created_at.isdigit():
                                    created_timestamp = int(created_at)
                                    # 如果大于10^12，认为是毫秒时间戳
                                    if created_timestamp > 10**12:
                                        created_timestamp = created_timestamp // 1000
                                elif isinstance(created_at, (int, float)):
                                    created_timestamp = int(created_at)
                                else:
                                    # 尝试解析ISO格式时间字符串
                                    import re
                                    # 匹配 YYYY-MM-DDTHH:MM:SS 格式
                                    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', str(created_at))
                                    if match:
                                        # 处理 Z 后缀
                                        time_str = match.group(1).replace('T', ' ')
                                        if 'Z' in created_at:
                                            time_str += ' UTC'
                                        else:
                                            time_str += ' +00:00'
                                        dt = datetime.fromisoformat(time_str.replace(' UTC', '+00:00'))
                                        created_timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())
                                    else:
                                        # 无法解析，跳过这个检查
                                        created_timestamp = start_timestamp + 1

                                # 如果早于起始时间，跳过
                                if created_timestamp < start_timestamp:
                                    # print(f"跳过旧市场 {market.get('id', 'unknown')}: {created_at}")
                                    continue
                            except Exception as e:
                                print(f"解析时间错误 {market.get('id', 'unknown')}: {e}")
                                # 如果解析失败，假设在时间范围内
                                pass

                        # Parse outcomes for answer1 and answer2
                        outcomes_str = market.get('outcomes', '[]')
                        if isinstance(outcomes_str, str):
                            outcomes = json.loads(outcomes_str)
                        else:
                            outcomes = outcomes_str
                        
                        answer1 = outcomes[0] if len(outcomes) > 0 else ''
                        answer2 = outcomes[1] if len(outcomes) > 1 else ''
                        
                        # Parse clobTokenIds for token1 and token2
                        clob_tokens_str = market.get('clobTokenIds', '[]')
                        if isinstance(clob_tokens_str, str):
                            clob_tokens = json.loads(clob_tokens_str)
                        else:
                            clob_tokens = clob_tokens_str
                        
                        token1 = clob_tokens[0] if len(clob_tokens) > 0 else ''
                        token2 = clob_tokens[1] if len(clob_tokens) > 1 else ''
                        
                        # Check for negative risk indicators
                        neg_risk = market.get('negRiskAugmented', False) or market.get('negRiskOther', False)
                        
                        # Create row with required columns
                        question_text = market.get('question', '') or market.get('title', '')
                        
                        # Get ticker from events if available
                        ticker = ''
                        if market.get('events') and len(market.get('events', [])) > 0:
                            ticker = market['events'][0].get('ticker', '')
                        
                        row = [
                            market.get('createdAt', ''),
                            market.get('id', ''),
                            question_text,
                            answer1,
                            answer2,
                            neg_risk,
                            market.get('slug', ''),
                            token1,
                            token2,
                            market.get('conditionId', ''),
                            market.get('volume', ''),
                            ticker,
                            market.get('closedTime', '')
                        ]
                        
                        writer.writerow(row)
                        batch_count += 1
                        
                    except (ValueError, KeyError, json.JSONDecodeError) as e:
                        print(f"Error processing market {market.get('id', 'unknown')}: {e}")
                        continue
                
                total_fetched += batch_count
                current_offset += batch_count  # Increment by actual records processed

                print(f"Processed {batch_count} markets. Total new: {total_fetched}. Next offset: {current_offset}")

                # Check if we should stop
                # If we got fewer markets than expected from API, might be near the end
                # But we need to check if any valid markets were processed
                if len(markets) < batch_size:
                    # API returned less than batch_size - might be at the end
                    if batch_count == 0:
                        # No valid markets processed in this batch - truly at the end
                        print(f"API returned {len(markets)} markets, none valid (all before time range). Reached end.")
                        break
                    else:
                        # Some valid markets processed - continue to next batch
                        # This batch might have mixed old/new markets
                        print(f"API returned {len(markets)} markets, processed {batch_count}. Continuing...")
                        continue
                elif batch_count == 0:
                    # Got full batch_size but none were valid (all before time range)
                    # This means we've gone past the time range
                    print(f"Received {len(markets)} markets but none within time range. Stopping.")
                    break
                
            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}")
                print(f"Retrying in 5 seconds...")
                import time
                time.sleep(5)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                print(f"Retrying in 3 seconds...")
                import time
                time.sleep(3)
                continue
    
    print(f"\nCompleted! Fetched {total_fetched} new markets.")
    print(f"Data saved to: {csv_filename}")
    print(f"Total records: {current_offset}")

# if __name__ == "__main__":
#     update_markets(batch_size=500)