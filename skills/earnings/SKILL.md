# Earnings Skill - 财报监控 Skill

## 概述

财报监控 skill 用于管理美股和港股的财报提醒和简报系统。

## 触发词

- `关注`
- `取消关注`
- `删除`
- `财报`
- `earnings`
- `watchlist`
- `添加`
- `移除`
- `异动`
- `阈值`
- `提醒`
- `灵敏度`

## 功能

### 1. 添加关注

#### 美股
- "关注 AAPL"
- "添加关注 NVDA"
- "添加美股 TSLA 特斯拉"
- "watch AAPL"

#### 港股
- "关注 腾讯"
- "添加关注 0700"
- "添加港股 9988 阿里巴巴"
- "watch 0700"

**注意**: 添加港股时，如果知道财报日期，可以提供格式 "YYYY-MM-DD"，否则使用默认日期。

### 2. 删除关注

- "取消关注 BABA"
- "删除关注 AAPL"
- "unwatch NVDA"
- "remove 0700"

### 3. 查看关注列表

- "我关注了哪些股票"
- "列出关注"
- "查看关注列表"
- "watchlist"
- "我关注的股票"

### 4. 查看财报状态

- "财报提醒状态"
- "下次财报是什么时候"
- "财报时间"
- "earnings status"

### 5. 手动触发检查

- "检查财报"
- "更新财报数据"
- "刷新财报"
- "check earnings"

### 6. 生成财报简报

- "生成 AAPL 财报简报"
- "查看 0700 财报"
- "财报简报 NVDA"
- "summary TSLA"

### 7. 异动提醒管理

#### 修改阈值
- "异动阈值改为 3%"
- "把阈值调到 5%"
- "设置异动阈值为 2.5%"
- "threshold 4"

#### 开关提醒
- "异动提醒关闭"
- "关闭股价提醒"
- "异动提醒开启"
- "开启异动监控"

#### 查看状态
- "异动提醒状态"
- "查看阈值配置"
- "alert status"

#### 调整灵敏度
- "股价提醒灵敏度调高" → 降低阈值（如从 5% 降到 3%）
- "异动提醒灵敏度调低" → 提高阈值（如从 3% 升到 8%）

## 实现指令

Agent 应该使用 `scripts/manage_watchlist.py` 脚本来执行具体操作。

### 脚本命令格式

```bash
# 添加美股
python3 ~/.openclaw/scripts/manage_watchlist.py add-us <symbol> [name]

# 添加港股
python3 ~/.openclaw/scripts/manage_watchlist.py add-hk <symbol> <name> [date]

# 删除美股
python3 ~/.openclaw/scripts/manage_watchlist.py remove-us <symbol>

# 删除港股
python3 ~/.openclaw/scripts/manage_watchlist.py remove-hk <symbol>

# 列出关注
python3 ~/.openclaw/scripts/manage_watchlist.py list

# 手动检查
python3 ~/.openclaw/scripts/manage_watchlist.py check

# 生成简报
python3 ~/.openclaw/scripts/manage_watchlist.py summary <symbol>

# 异动提醒 - 设置阈值
python3 ~/.openclaw/scripts/manage_watchlist.py threshold <value>

# 异动提醒 - 开启
python3 ~/.openclaw/scripts/manage_watchlist.py threshold-on

# 异动提醒 - 关闭
python3 ~/.openclaw/scripts/manage_watchlist.py threshold-off

# 异动提醒 - 查看状态
python3 ~/.openclaw/scripts/manage_watchlist.py alert-status
```

## 自然语言处理指南

### 识别股票类型

- **美股**: 字母代码 (AAPL, NVDA, TSLA 等)
- **港股**: 4 位数字代码 (0700, 9988, 2513 等)

### 中文公司名映射

常见中文名到股票代码的映射：
- 苹果 / Apple → AAPL
- 微软 / Microsoft → MSFT
- 谷歌 / Google → GOOGL
- 亚马逊 / Amazon → AMZN
- 英伟达 / Nvidia → NVDA
- Meta / Facebook → META
- 特斯拉 / Tesla → TSLA
- 阿里巴巴 → BABA (美股) / 9988 (港股)
- 腾讯 → 0700
- 智谱AI → 2513
- MiniMax → 0100

### 日期格式

财报日期应为 YYYY-MM-DD 格式，如 2026-05-15。

## 配置文件路径

- 配置: `~/.openclaw/workspace/earnings-alert/config.json`
- 数据库: `~/.openclaw/workspace/earnings-alert/data/earnings.db`
- 港股数据: `~/.openclaw/workspace/earnings-alert/src/fetch_hk.py`

### config.json 结构

```json
{
  "us_stocks": ["AAPL", "NVDA"],
  "hk_stocks": [{"code": "0700", "name": "腾讯控股"}],
  "price_alert": {
    "enabled": true,
    "threshold": 5.0,
    "check_interval_minutes": 15
  }
}
```

## 注意事项

1. 添加港股时需要同时更新 `src/fetch_hk.py` 中的 `HK_EARNINGS_DATA`
2. 如果不知道港股财报日期，可以设为未来一个日期或询问用户
3. 美股财报数据会自动从 Alpha Vantage API 获取
4. 生成简报需要有效的 API key 配置
5. 异动提醒阈值默认为 5%，可根据个人偏好调整
6. 调高灵敏度会降低阈值，调低灵敏度会提高阈值

## 示例对话

```
用户: 关注 NVDA
Agent: 已添加美股关注: NVDA (英伟达)

用户: 关注腾讯
Agent: 已添加港股关注: 腾讯控股 (0700)

用户: 我关注了哪些股票?
Agent: [调用 list 命令显示列表]

用户: 取消关注 BABA
Agent: 已删除美股关注: BABA

用户: 生成 AAPL 财报简报
Agent: 正在生成 Apple Inc. (AAPL) 的财报简报...

用户: 异动阈值改为 3%
Agent: 涨跌幅阈值已设置为 3%
       异动提醒已开启

用户: 股价提醒灵敏度调高
Agent: 涨跌幅阈值已设置为 2%
       异动提醒已开启

用户: 异动提醒状态
Agent: 🔔 异动提醒配置:
         状态: ✓ 已开启
         阈值: ±3.0%
         检查间隔: 15 分钟

用户: 异动提醒关闭
Agent: 异动提醒已关闭
```
