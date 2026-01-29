from web3 import Web3

# 配置Web3
RPC_PROVIDER = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_PROVIDER))

# 验证连接
if not w3.is_connected():
    raise Exception("无法连接到Polygon网络")

# CTF合约地址
CTF_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# CTF合约ABI (简化版)
CTF_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "collateralToken", "type": "address"},
            {"internalType": "bytes32", "name": "parentCollectionId", "type": "bytes32"},
            {"internalType": "bytes32", "name": "conditionId", "type": "bytes32"},
            {"internalType": "uint256[]", "name": "indexSets", "type": "uint256[]"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "mergePositions",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# 创建合约实例
contract = w3.eth.contract(address=CTF_ADDRESS, abi=CTF_ABI)

def merge_position_on_chain(condition_id, amount_wei, private_key):
    """
    在链上调用mergePosition
    注意：这里需要支付Gas
    """
    try:
        account = w3.eth.account.from_key(private_key)

        # 构建交易
        tx = contract.functions.mergePositions(
            USDC_ADDRESS,              # 结算货币地址
            b'\x00' * 32,             # 父集合ID，通常为0
            condition_id,             # 市场唯一条件ID
            [1, 2],                   # 分区索引：[1,2]代表合并Yes和No
            amount_wei                # 合并的数量
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'chainId': 137  # Polygon主网ID
        })

        # 签名交易
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"✅ Merge TX已发送: {w3.to_hex(tx_hash)}")
        return w3.to_hex(tx_hash)

    except Exception as e:
        print(f"❌ Merge失败: {e}")
        raise
