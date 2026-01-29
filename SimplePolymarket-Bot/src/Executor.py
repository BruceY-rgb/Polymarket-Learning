import os
import asyncio # 引入异步库，更适合IO密集型的任务
from py_clob_client import ClobClient
from py_clob_client.clob_types import OrderArgs

# 客户端初始化 - 延迟加载以避免在模块导入时执行
_client = None

def get_client():
    """获取或创建CLOB客户端实例"""
    global _client
    if _client is None:
        key = os.getenv("PRIVATE_KEY")
        chain_id = 137
        host = "https://clob.polymarket.com"

        if not key:
            raise ValueError("未设置PRIVATE_KEY环境变量")

        _client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1)
        _client.set_api_creds(_client.create_or_derive_api_creds())

    return _client

async def place_order_safe(order_args):
    """
    封装单个下单动作，增加异常捕获
    """
    try:
        client = get_client()
        resp = client.create_and_post_order(order_args)
        return {"status":"success", "resp":resp}
    except Exception as e:
        return {"status":"failed", "error":str(e)}
    
async def execute_arbitrage(token_yes, token_no, price_yes, price_no, size):
    """
    并发下单+风险对冲检查
    """

    print("发起并发套利: Yes@(price_yes), No@(price_no), Size:(size)")

    # 准备两个订单的参数
    order_yes = OrderArgs(
        price = price_yes,
        size=size,
        side="BUY",
        token_id=token_yes
    )

    order_no = OrderArgs(
        price = price_no,
        size=size,
        side="BUY",
        token_id=token_no
    )

    # 使用asyncio.gather同时发出两个请求
    # 这可以显著降低因为先后顺序导致的风险敞口

    results = await asyncio.gather(
        place_order_safe(order_yes),
        place_order_safe(order_no),
        return_exceptions=True # 保证并发任务之间互不干扰 
    )

    res_yes, res_no = results

    # --- 逻辑判定与风险处理 ---
    
    # 情况1：双边都成功
    if res_yes["status"] == "success" and res_no["status"] == "success":
        print("✅ 套利指令已全部成交，等待利润到账。")
        return True

    # 情况2：致命的单边风险
    elif res_yes["status"] == "success" and res_no["status"] == "failed":
        print(f"⚠️ 警报：Yes成交但No失败！错误: {res_no['error']}")
        print("🚨 正在启动紧急避险：尝试撤单或市价卖出Yes...")
        # 此处应调用回滚逻辑，例如：client.cancel_order(...)
        return False

    elif res_no["status"] == "success" and res_yes["status"] == "failed":
        print(f"⚠️ 警报：No成交但Yes失败！错误: {res_yes['error']}")
        print("🚨 正在启动紧急避险：尝试撤单或市价卖出No...")
        return False

    # 情况3：两边都失败
    else:
        print("❌ 交易全部失败，未产生损失。")
        return False
    
# 运行入口
if __name__ == "__main__":
    # 模拟数据
    asyncio.run(execute_arbitrage(
        "TOKEN_YES_ID",
        "TOKEN_NO_ID",
        0.45, 0.53, 100
    ))