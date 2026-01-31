# Polymarket 数据项目配置说明

## 项目概述

本项目是一个用于获取、处理和分析 Polymarket 交易数据的综合数据管道系统。

## 配置文件说明

### pyproject.toml

项目的核心配置文件，包含以下关键部分：

#### 项目元数据
```toml
[project]
name = "polymarket-data"
version = "版本号"
description = "Polymarket 数据分析工具"
```

#### 依赖管理

**主要依赖**：
- `polars` - 高性能 DataFrame 库，用于快速数据处理
- `pandas` - 数据分析库，提供易用的数据结构
- `gql` - GraphQL 客户端，用于 Goldsky API 交互
- `requests` - HTTP 请求库，访问 Polymarket API
- `flatten-json` - JSON 数据扁平化工具

**可选依赖**（开发用）：
- `jupyter` - 交互式笔记本环境
- `notebook` - Jupyter 经典笔记本界面
- `ipykernel` - Python 内核

#### 构建配置
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### uv.lock

**用途**：锁定依赖版本，确保环境一致性

**特点**：
- 自动管理依赖树
- 快速安装
- 跨平台支持

## 环境配置

### 虚拟环境设置

**使用 UV 创建环境**：
```bash
# 创建虚拟环境
uv venv

# 激活环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

**使用 .venv 目录**：
项目使用 `.venv` 作为默认虚拟环境目录，已在 `.gitignore` 中配置。

### 依赖安装

```bash
# 安装所有依赖
uv sync

# 安装开发依赖
uv sync --extra dev

# 仅安装运行时依赖
uv sync --no-dev
```

## 数据目录结构

```
poly_data/
├── markets.csv                    # 主要市场数据集
├── missing_markets.csv            # 缺失市场数据集（自动生成）
├── goldsky/
│   └── orderFilled.csv           # Goldsky 订单事件
├── processed/
│   └── trades.csv                # 处理后的交易数据
└── [其他数据文件...]
```

## API 配置

### Polymarket API
- **基础 URL**：`https://gamma-api.polymarket.com/markets`
- **用途**：获取市场数据
- **特点**：支持分页、排序、筛选

### Goldsky GraphQL
- **用途**：获取订单成交事件
- **特点**：支持 GraphQL 查询，自动处理分页

## 性能优化配置

### Polars 配置
```python
import polars as pl

# 设置显示行数
pl.Config.set_tbl_rows(25)

# 设置显示列数
pl.Config.set_tbl_cols(-1)  # 显示所有列

# 设置显示宽度
pl.Config.set_tbl_width_chars(1000)  # 更宽的显示
```

### 流式处理
```python
# 使用流式处理大型 CSV 文件
df = pl.scan_csv("large_file.csv").collect(streaming=True)
```

## 错误处理配置

### 网络重试
- **最大重试次数**：3 次
- **指数退避**：2 秒起步
- **速率限制**：429 错误时等待 10 秒
- **服务器错误**：500 错误时等待 5 秒

### 数据验证
- 检查 CSV 文件完整性
- 验证 JSON 响应格式
- 处理缺失字段

## 平台钱包配置

以下钱包地址被识别为平台钱包（用于特殊处理）：
- `0xc5d563a36ae78145c45a50134d48a1215220f80a`
- `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e`

配置位置：`poly_utils/utils.py`

## 数据模式配置

### 市场数据字段
| 字段 | 类型 | 描述 |
|------|------|------|
| createdAt | datetime | 创建时间 |
| id | string | 市场 ID |
| question | string | 市场问题 |
| answer1/answer2 | string | 结果选项 |
| neg_risk | boolean | 负风险标志 |
| market_slug | string | 市场别名 |
| token1/token2 | string | 代币 ID |
| condition_id | string | 条件 ID |
| volume | float | 交易量 |
| ticker | string | 行情代码 |
| closedTime | datetime | 关闭时间 |

### 交易数据字段
| 字段 | 类型 | 描述 |
|------|------|------|
| timestamp | datetime | 时间戳 |
| market_id | string | 市场 ID |
| maker/taker | string | 发起者/接受者地址 |
| nonusdc_side | string | 非 USDC 方 |
| maker_direction | string | 发起者方向（BUY/SELL） |
| taker_direction | string | 接受者方向（BUY/SELL） |
| price | float | 价格 |
| usd_amount | float | 美元金额 |
| token_amount | float | 代币金额 |
| transactionHash | string | 交易哈希 |

## 监控和日志

### 进度跟踪
- 显示当前处理的偏移量
- 显示已处理记录数
- 显示剩余工作量估算

### 状态输出
- 文件创建和加载状态
- API 响应状态
- 错误和警告信息

## 扩展配置

### 自定义批处理大小
```python
# 在调用时指定
update_markets(batch_size=500)
update_goldsky(batch_size=1000)
```

### 自定义输出文件
```python
# 指定自定义文件名
update_markets(csv_filename="custom_markets.csv")
```

## 故障排除

### 常见问题

1. **文件不存在错误**
   - 检查数据目录结构
   - 确认权限设置

2. **API 速率限制**
   - 增加延迟时间
   - 减少批处理大小

3. **内存不足**
   - 使用流式处理
   - 分批处理数据

4. **数据不一致**
   - 重新运行管道
   - 检查数据快照完整性

### 调试模式
```python
# 启用详细输出
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 性能基准

### 典型处理速度
- 市场数据获取：约 500 个/批次
- 订单事件获取：约 1000 个/批次
- 数据处理：取决于数据量大小

### 资源使用
- 内存：建议至少 4GB
- 存储：根据数据量调整（完整数据集约几 GB）
- 网络：稳定互联网连接

## 安全注意事项

- API 密钥安全管理
- 用户钱包地址隐私保护
- 数据传输加密
- 定期更新依赖包

## 许可证

项目采用宽松许可证，允许自由使用和修改。
