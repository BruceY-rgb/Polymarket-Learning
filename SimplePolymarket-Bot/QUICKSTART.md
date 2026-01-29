# Polymarket套利系统 - 快速启动指南

## 🚀 快速开始

### 1. 激活虚拟环境

```bash
source myenv/bin/activate
```

### 2. 安装依赖（如果需要）

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制模板文件
cp .env.example .env

# 编辑.env文件，填入您的私钥
# ⚠️ 警告: 绝不要分享或提交此文件到版本控制系统！
```

**必需的.env配置**:
```bash
PRIVATE_KEY=your_wallet_private_key_here
```

**可选的配置**:
```bash
ARBITRAGE_THRESHOLD=0.005    # 0.5% 套利阈值
DEFAULT_ORDER_SIZE=100       # 默认订单大小
VERBOSE=false                 # 详细日志
```

### 4. 运行测试

```bash
python3 test.py
```

确保所有测试通过后再进行下一步。

### 5. 启动系统

```bash
python3 main.py
```

## 📋 使用流程

系统启动后会自动：

1. **扫描市场** - 从Polymarket API获取活跃市场
2. **监控订单簿** - 实时监控价格变动
3. **检测套利** - 当Yes+No成本低于阈值时触发
4. **执行交易** - 自动下单进行套利

## ⚠️ 安全提醒

1. **使用测试网络**: 首次使用时，建议先在Amoy测试网络上测试
2. **专用钱包**: 不要使用主要资产的钱包，使用专用测试钱包
3. **限额设置**: 从小额开始测试，逐步增加
4. **监控日志**: 仔细观察交易日志，确保按预期工作

## 🐛 故障排除

### 常见问题

**Q: WebSocket连接失败**
```bash
# 检查网络连接
ping ws-subscriptions-clob.polymarket.com

# 防火墙可能阻止连接，检查代理设置
```

**Q: 交易执行失败**
```bash
# 检查私钥是否正确
# 确认账户有足够余额
# 检查Gas价格是否合理
```

**Q: 检测不到套利机会**
```bash
# 降低套利阈值
ARBITRAGE_THRESHOLD=0.003

# 检查市场流动性
# 某些市场可能流动性不足
```

## 📞 获取帮助

- 查看详细文档: `README.md`
- 运行诊断测试: `python3 test.py`
- 启用详细日志: `VERBOSE=true python3 main.py`

---

**免责声明**: 此系统用于教育目的。加密货币交易存在重大风险，使用前请充分了解风险。
