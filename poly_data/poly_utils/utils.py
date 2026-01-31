import os
import csv
import json
import requests
import time
from typing import List
import polars as pl

PLATFORM_WALLETS = ['0xc5d563a36ae78145c45a50134d48a1215220f80a', '0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e']


def get_markets(main_file: str = "markets.csv", missing_file: str = "missing_markets.csv"):
    """
    加载并合并两个文件中的市场，去重，并按 createdAt 排序
    返回按创建日期排序的合并 Polars DataFrame
    """
    import polars as pl
    
    # 模式覆盖用于长令牌 ID
    schema_overrides = {
        "token1": pl.Utf8,      # 76 位数字 ID → 字符串
        "token2": pl.Utf8,
    }
    
    dfs = []
    
    # 加载主市场文件
    if os.path.exists(main_file):
        main_df = pl.scan_csv(main_file, schema_overrides=schema_overrides).collect(streaming=True)
        dfs.append(main_df)
        print(f"从 {main_file} 加载了 {len(main_df)} 个市场")

    # 加载缺失市场文件
    if os.path.exists(missing_file):
        missing_df = pl.scan_csv(missing_file, schema_overrides=schema_overrides).collect(streaming=True)
        dfs.append(missing_df)
        print(f"从 {missing_file} 加载了 {len(missing_df)} 个市场")

    if not dfs:
        print("未找到市场文件！")
        return pl.DataFrame()

    # 合并、去重并排序
    combined_df = (
        pl.concat(dfs)
        .unique(subset=['id'], keep='first')
        .sort('createdAt')
    )
    
    print(f"合并总计：{len(combined_df)} 个唯一市场（按 createdAt 排序）")
    return combined_df


def update_missing_tokens(missing_token_ids: List[str], csv_filename: str = "missing_markets.csv"):
    """
    获取缺失令牌 ID 的市场数据并保存到单独的 CSV 文件

    Args:
        missing_token_ids: 要获取的令牌 ID 列表
        csv_filename: 保存缺失市场的 CSV 文件（默认：missing_markets.csv）
    """
    if not missing_token_ids:
        print("没有要获取的缺失令牌")
        return

    print(f"正在获取 {len(missing_token_ids)} 个缺失令牌...")
    
    # 与主 markets.csv 相同的头部
    headers = [
        'createdAt', 'id', 'question', 'answer1', 'answer2', 'neg_risk',
        'market_slug', 'token1', 'token2', 'condition_id', 'volume', 'ticker', 'closedTime'
    ]
    
    # 检查文件是否存在以确定是否需要头部
    file_exists = os.path.exists(csv_filename)

    new_markets = []
    processed_market_ids = set()

    # 如果文件存在，读取现有市场 ID 以避免重复
    if file_exists:
        try:
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('id'):
                        processed_market_ids.add(row['id'])
            print(f"在 {csv_filename} 中找到 {len(processed_market_ids)} 个现有市场")
        except Exception as e:
            print(f"读取现有文件错误：{e}")

    for token_id in missing_token_ids:
        print(f"正在获取令牌的市场：{token_id}")
        
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                response = requests.get(
                    'https://gamma-api.polymarket.com/markets',
                    params={'clob_token_ids': token_id},
                    timeout=30
                )
                
                if response.status_code == 429:
                    print(f"达到速率限制 - 等待 10 秒...")
                    time.sleep(10)
                    continue
                elif response.status_code != 200:
                    print(f"令牌 {token_id} 的 API 错误 {response.status_code}")
                    retry_count += 1
                    time.sleep(2)
                    continue

                markets = response.json()

                if not markets:
                    print(f"令牌 {token_id} 未找到市场")
                    break

                market = markets[0]
                market_id = market.get('id', '')

                # 如果我们已经有这个市场，跳过
                if market_id in processed_market_ids:
                    print(f"市场 {market_id} 已存在 - 跳过")
                    break

                # 解析 clobTokenIds
                clob_tokens_str = market.get('clobTokenIds', '[]')
                if isinstance(clob_tokens_str, str):
                    clob_tokens = json.loads(clob_tokens_str)
                else:
                    clob_tokens = clob_tokens_str

                if len(clob_tokens) < 2:
                    print(f"令牌 {token_id} 的令牌数据无效")
                    break
                
                token1, token2 = clob_tokens[0], clob_tokens[1]

                # 解析结果
                outcomes_str = market.get('outcomes', '[]')
                if isinstance(outcomes_str, str):
                    outcomes = json.loads(outcomes_str)
                else:
                    outcomes = outcomes_str

                answer1 = outcomes[0] if len(outcomes) > 0 else 'YES'
                answer2 = outcomes[1] if len(outcomes) > 1 else 'NO'

                # 检查负风险
                neg_risk = market.get('negRiskAugmented', False) or market.get('negRiskOther', False)

                # 如果可用，从事件中获取行情代码
                ticker = ''
                if market.get('events') and len(market.get('events', [])) > 0:
                    ticker = market['events'][0].get('ticker', '')

                question_text = market.get('question', '') or market.get('title', '')

                # 创建市场行
                row = [
                    market.get('createdAt', ''),
                    market_id,
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
                
                new_markets.append(row)
                processed_market_ids.add(market_id)
                print(f"成功获取令牌 {token_id} 的市场 {market_id}")
                break

            except Exception as e:
                print(f"获取令牌 {token_id} 错误：{e}")
                retry_count += 1
                time.sleep(2)

        if retry_count >= max_retries:
            print(f"经过 {max_retries} 次重试后获取令牌 {token_id} 失败")

        # 请求之间的小延迟
        time.sleep(0.5)

    if not new_markets:
        print("没有要添加的新市场")
        return

    # 将新市场写入文件
    mode = 'a' if file_exists else 'w'
    with open(csv_filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # 仅在新文件时写入头部
        if not file_exists:
            writer.writerow(headers)

        writer.writerows(new_markets)

    print(f"向 {csv_filename} 添加了 {len(new_markets)} 个新市场")
    print(f"文件中现有市场总数：{len(processed_market_ids)}")

