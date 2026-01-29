import requests # 查询gamma API元数据
import time # 计时
import json

def fetch_arbitrage_candidates():
    """
    从Gamma API获取活跃且开启丁单薄的市场列表
    """
    url = "https://gamma-api.polymarket.com/markets"
    markets = []
    limit = 100
    offset = 0

    while True:
        params = {
            "limit":limit, # 控制单页返回数据的最大量
            "offset": offset,
            "active": "true",
            "closed": "false",
            "enable_order_book": "true",
            "order": "volume:desc" #按交易量排序，优先关注热点
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break;

            markets.extend(data) # 先填充数据，确保所有数据都能被读到
            
            # 如果数量少于limit，说明已经到末尾

            if len(data) < limit:
                break

            offset+=limit
            time.sleep(0.1) # 礼貌性限流

        except Exception as e:
            print(f"Error fetching markets: {e}")
            break
    return markets

# 解析市场数据，提取Token IDs

def parse_market_metadata(market):
    # 二元市场通常有两个Token: Yes和No
    # 负风险市场可能有多个
    tokens = market.get('clobTokenIds') # 该市场在CLOB中每一个代币的唯一数字标识
    condition_id = market.get('conditionId') # CTF中定义的该事件的唯一标识符
    # 它将几个不同的 TokenID 绑定在一起。比如它告诉合约：这两个 Token 是属于“特朗普是否获胜”这个同一个事件的。
    question = market.get('question') # 给人类看的描述语言，该预测市场的具体内容
    # 例如："Will Bitcoin reach $100,000 by the end of 2025?"（比特币在2025年底前会达到10万美元吗？）

    return{
        "question": question,
        "condition_id": condition_id,
        "token_ids": json.loads(tokens) if isinstance(tokens, str) else tokens
        # Web API交互中，数据通常以字符串的形式在网络上传输，Python无法直接操作字符串内部的逻辑，所以在遇见字符串时要将其转化为列表
    }
            