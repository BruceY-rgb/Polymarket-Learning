# Polymarket 数据分析

一个用于获取、处理和分析 Polymarket 交易数据的综合数据管道系统。该系统收集市场信息、订单成交事件，并将它们处理成结构化的交易数据。

## 快速下载

**首次用户**：请下载 [最新数据快照](https://polydata-archive.s3.us-east-1.amazonaws.com/archive.tar.xz) 并在首次运行前将其解压到主仓库目录。这将为您节省超过2天的初始数据收集时间。

## 概述

本管道执行三个主要操作：

1. **市场数据收集** - 获取所有 Polymarket 市场的元数据
2. **订单事件抓取** - 从 Goldsky 子图收集订单成交事件
3. **交易处理** - 将原始订单事件转换为结构化交易数据

## 安装

本项目使用 [UV](https://docs.astral.sh/uv/) 进行快速、可靠的包管理。

### 安装 UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 安装依赖

```bash
# 安装所有依赖
uv sync

# 安装开发依赖（包括 Jupyter 等）
uv sync --extra dev
```

## 快速开始

```bash
# 使用 UV 运行（推荐）
uv run python update_all.py

# 或先激活虚拟环境
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python update_all.py
```

这将按顺序运行所有三个管道阶段：
- 从 Polymarket API 更新市场
- 从 Goldsky 更新订单成交事件
- 将新订单处理为交易

## 项目结构

```
poly_data/
├── update_all.py              # 主协调脚本
├── update_utils/              # 数据收集模块
│   ├── update_markets.py      # 从 Polymarket API 获取市场
│   ├── update_goldsky.py      # 从 Goldsky 抓取订单事件
│   └── process_live.py        # 将订单处理为交易
├── poly_utils/                # 实用工具函数
│   └── utils.py               # 市场加载和缺失令牌处理
├── markets.csv                # 主要市场数据集
├── missing_markets.csv        # 从交易中发现的市场（自动生成）
├── goldsky/                   # 订单成交事件（自动生成）
│   └── orderFilled.csv
└── processed/                 # 处理后的交易数据（自动生成）
    └── trades.csv
```

## 数据文件

### markets.csv
市场元数据包括：
- 市场问题、结果和代币
- 创建/关闭时间和别名
- 交易量和条件 ID
- 负风险指标

**字段**：`createdAt`、`id`、`question`、`answer1`、`answer2`、`neg_risk`、`market_slug`、`token1`、`token2`、`condition_id`、`volume`、`ticker`、`closedTime`

### goldsky/orderFilled.csv
原始订单成交事件，包括：
- 发起者/接受者地址和资产 ID
- 成交数量和交易哈希
- Unix 时间戳

**字段**：`timestamp`、`maker`、`makerAssetId`、`makerAmountFilled`、`taker`、`takerAssetId`、`takerAmountFilled`、`transactionHash`

### processed/trades.csv
结构化交易数据，包括：
- 市场 ID 映射和交易方向
- 价格、美元金额和代币金额
- 发起者/接受者角色和交易详情

**字段**：`timestamp`、`market_id`、`maker`、`taker`、`nonusdc_side`、`maker_direction`、`taker_direction`、`price`、`usd_amount`、`token_amount`、`transactionHash`

## 管道阶段

### 1. 更新市场 (`update_markets.py`)

按时间顺序从 Polymarket API 获取所有市场。

**功能**：
- 从最后偏移自动恢复（幂等）
- 速率限制和错误处理
- 批量获取（每次请求 500 个市场）

**用法**：
```bash
uv run python -c "from update_utils.update_markets import update_markets; update_markets()"
```

### 2. 更新 Goldsky (`update_goldsky.py`)

从 Goldsky 子图 API 抓取订单成交事件。

**功能**：
- 自动从最后时间戳恢复
- 处理带分页的 GraphQL 查询
- 事件去重

**用法**：
```bash
uv run python -c "from update_utils.update_goldsky import update_goldsky; update_goldsky()"
```

### 3. 处理实时交易 (`process_live.py`)

将原始订单事件处理为结构化交易。

**功能**：
- 使用令牌查找将资产 ID 映射到市场
- 计算价格和交易方向
- 识别买入/卖出方向
- 通过从交易中发现来处理缺失的市场
- 从最后检查点增量处理

**用法**：
```bash
uv run python -c "from update_utils.process_live import process_live; process_live()"
```

**处理逻辑**：
- 识别每笔交易中的非 USDC 资产
- 映射到市场和结果代币（token1/token2）
- 确定发起者/接受者方向（买入/卖出）
- 计算价格为每个结果代币的 USDC 数量
- 将金额从原始单位转换（除以 10^6）

## 依赖

依赖通过 `pyproject.toml` 管理，使用 `uv sync` 自动安装。

**主要库**：
- `polars` - 快速 DataFrame 操作
- `pandas` - 数据操作
- `gql` - Goldsky 的 GraphQL 客户端
- `requests` - 对 Polymarket API 的 HTTP 请求
- `flatten-json` - 嵌套响应的 JSON 扁平化

**开发依赖**（可选，使用 `--extra dev` 安装）：
- `jupyter` - 交互式笔记本
- `notebook` - Jupyter 笔记本界面
- `ipykernel` - Jupyter 的 Python 内核

## 功能

### 可恢复操作
所有阶段自动从上次中断的地方恢复：
- **市场**：计算现有 CSV 行数以设置偏移
- **Goldsky**：从 orderFilled.csv 读取最后时间戳
- **处理**：查找最后处理的交易哈希

### 错误处理
- 网络故障时自动重试
- 速率限制检测和退避
- 服务器错误（500）处理
- 缺失数据的优雅降级

### 缺失市场发现
处理阶段自动发现初始 markets.csv 中没有的市场（例如，上次更新后创建的市场）并通过 Polymarket API 获取它们，保存到 `missing_markets.csv`。

## 数据模式详情

### 交易方向逻辑
- **接受者方向**：支付 USDC 时为买入，接收 USDC 时为卖出
- **发起者方向**：与接受者方向相反
- **价格**：始终表示为每个结果代币的 USDC 数量

### 资产映射
- `makerAssetId`/`takerAssetId` 为 "0" 代表 USDC
- 非零 ID 是结果代币 ID（markets 中的 token1/token2）
- 每笔交易涉及 USDC 和一个结果代币

## 注意事项

- 所有金额都规范化为标准十进制格式（除以 10^6）
- 时间戳从 Unix 纪元转换为 datetime
- 平台钱包（`0xc5d563a36ae78145c45a50134d48a1215220f80a`、`0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e`）在 `poly_utils/utils.py` 中追踪
- 负风险市场在市场数据中标记

## 故障排除

**问题**：处理期间找不到市场
**解决方案**：先运行 `update_markets()`，或让 `process_live()` 自动发现

**问题**：重复交易
**解决方案**：去重是自动的 - 如果需要可以从头重新运行处理

**问题**：速率限制
**解决方案**：管道使用指数退避自动处理

## 分析

### 加载数据

```python
import pandas as pd
import polars as pl
from poly_utils import get_markets, PLATFORM_WALLETS

# 加载市场
markets_df = get_markets()

# 加载交易
df = pl.scan_csv("processed/trades.csv").collect(streaming=True)
df = df.with_columns(
    pl.col("timestamp").str.to_datetime().alias("timestamp")
)
```

### 按用户过滤交易

**重要**：过滤特定用户的交易时，按 `maker` 列过滤。即使看起来你只获得了用户是发起者的交易，这就是 Polymarket 在合约级别生成事件的方式。`maker` 列显示从该用户角度的交易，包括价格。

```python
USERS = {
    'domah': '0x9d84ce0306f8551e02efef1680475fc0f1dc1344',
    '50pence': '0x3cf3e8d5427aed066a7a5926980600f6c3cf87b3',
    'fhantom': '0x6356fb47642a028bc09df92023c35a21a0b41885',
    'car': '0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b',
    'theo4': '0x56687bf447db6ffa42ffe2204a05edaa20f55839'
}

# 获取特定用户的所有交易
trader_df = df.filter((pl.col("maker") == USERS['domah']))
```

## 许可证

随意使用
