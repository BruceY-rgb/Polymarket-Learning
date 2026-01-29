"""
Polymarket套利交易系统配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置"""

    # ==================== API配置 ====================
    # Gamma API配置
    GAMMA_API_URL = "https://gamma-api.polymarket.com/markets"
    GAMMA_API_LIMIT = 100

    # WebSocket配置
    WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

    # CLOB API配置
    CLOB_HOST = "https://clob.polymarket.com"
    CLOB_CHAIN_ID = 137  # Polygon主网

    # ==================== 区块链配置 ====================
    # RPC节点 (建议使用Alchemy或Infura等付费服务)
    RPC_PROVIDER = os.getenv("RPC_PROVIDER", "https://polygon-rpc.com")

    # CTF合约地址
    CTF_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

    # USDC合约地址 (Polygon)
    USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

    # ==================== 交易配置 ====================
    # 套利阈值 (例如0.005表示0.5%)
    ARBITRAGE_THRESHOLD = float(os.getenv("ARBITRAGE_THRESHOLD", "0.005"))

    # 默认订单大小
    DEFAULT_ORDER_SIZE = float(os.getenv("DEFAULT_ORDER_SIZE", "100"))

    # ==================== 安全配置 ====================
    # 私钥 (必须通过环境变量设置)
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")

    # ==================== 调试配置 ====================
    # 是否启用详细日志
    VERBOSE = os.getenv("VERBOSE", "false").lower() == "true"

    # ==================== 合约ABI ====================
    # CTF合约ABI (简化版，实际使用时应使用完整ABI)
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

    @classmethod
    def validate(cls):
        """验证配置是否有效"""
        errors = []

        if not cls.PRIVATE_KEY:
            errors.append("错误: 未设置PRIVATE_KEY环境变量")

        if cls.ARBITRAGE_THRESHOLD <= 0 or cls.ARBITRAGE_THRESHOLD >= 1:
            errors.append("错误: ARBITRAGE_THRESHOLD必须在0到1之间")

        if errors:
            raise ValueError("\n".join(errors))

        return True
