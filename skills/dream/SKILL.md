---
name: dream
version: "1.0.0"
description: "让小虾在空闲时自动「做梦」——整理记忆、产生洞察、发现关联。"
argument-hint: '/dream, /dream check, /dream force'
user-invocable: true
metadata:
  openclaw:
    emoji: "🌙"
    tags:
      - memory
      - ai-agent
      - insights
---

# Dream Skill - 小虾的「做梦」功能

让 AI Agent 在空闲时自动整理记忆、产生新洞察，就像人类睡眠时的潜意识处理。

## 功能概述

小虾会定期「做梦」，通过 5 种不同的模式处理记忆：

### 5 种做梦模式

| 模式 | 描述 | LLM |
|------|------|-----|
| **replay** | 重放最近记忆，强化重要信息 | 不需要 |
| **compression** | 压缩相似记忆，提炼精华 | 需要 |
| **connection** | 发现记忆间的隐藏联系 | 需要 |
| **extrapolation** | 预测 Alex 的可能需求 | 需要 |
| **insight** | 生成诗意梦境描述 | 需要 |

## 使用方式

### 手动触发

```bash
/dream              # 检查并执行做梦（如果条件满足）
/dream check        # 检查是否应该做梦
/dream force        # 强制执行一次做梦
```

### 自动触发

通过 cron job 每 2 小时自动运行一次：
```bash
# 每2小时检查一次是否需要做梦
0 */2 * * * cd /home/ubuntu/.openclaw && python3 scripts/dream_engine.py
```

## 触发条件

自动做梦需要满足：
- ✅ 自上次做梦后有新的记忆文件被修改
- ✅ 新增内容超过 100 字符
- ✅ 距离上次做梦至少 2 小时

## 梦境文件

每次做梦会生成一个梦境记录：
```
~/.openclaw/workspace/memory/dreams/YYYY-MM-DD_HHMM.md
```

包含：
- 做梦时间
- 选择的模式
- 处理的记忆量
- 梦境内容/洞察

## 查看梦境

### 查看最近的梦境
```bash
ls -lt ~/.openclaw/workspace/memory/dreams/ | head -5
cat ~/.openclaw/workspace/memory/dreams/$(ls -t ~/.openclaw/workspace/memory/dreams/ | head -1)
```

### 统计做梦次数
```bash
ls ~/.openclaw/workspace/memory/dreams/ | wc -l
```

## 模式选择逻辑

- **少量记忆** (< 5KB) → `replay` 模式
- **大量记忆** (> 10KB) → `compression` 模式
- **中等记忆** → 根据权重随机选择

## LLM 调用

- **主用**: Kimi API (kimi-k2-0905-preview)
- **回退**: DeepSeek (主用失败时)
- **限制**: 每次做梦最多 2 次 LLM 调用
- **成本控制**: replay 模式不调用 LLM

## 配置

所有配置在 `~/.openclaw/scripts/dream_engine.py` 的 `CONFIG` 字典中：

```python
CONFIG = {
    "min_new_memory_for_dream": 100,     # 最少新增字符
    "max_llm_calls_per_dream": 2,        # 最多 LLM 调用
    "small_memory_threshold": 5000,      # 小量记忆阈值
    "large_memory_threshold": 10000,     # 大量记忆阈值
    # ... 更多配置
}
```

## 工作流程

```
1. 检查就绪状态
   ↓
2. 读取最近的记忆文件
   ↓
3. 根据记忆量选择模式
   ↓
4. 执行对应模式的处理
   ↓
5. 生成梦境文件
   ↓
6. 如果需要，更新 MEMORY.md
   ↓
7. 更新做梦时间戳
```

## 设计参考

基于 Bitterbot-AI Dream Engine 的简化实现：
- 原版: 7 种模式 + 复杂信号机制
- 简化版: 5 种模式 + 简单触发条件

适配 OpenClaw 的轻量级设计。

## 注意事项

- ⚠️ 做梦是静默运行，只在发现重要洞察时通知
- ⚠️ replay 模式不调用 LLM，完全免费
- ⚠️ 其他模式会消耗 Kimi API 配额
- ⚠️ 如果记忆很少，可能会跳过做梦

## 示例输出

```
🌙 小虾开始做梦...
✅ 新增记忆 1234 字符，开始做梦...
📚 读取了 3 个记忆文件
🎭 选择做梦模式: insight
💾 梦境已保存: /home/ubuntu/.openclaw/workspace/memory/dreams/2026-04-03_0230.md
😊 做梦完成！
```

## 技术细节

- **语言**: Python 3
- **依赖**: requests, pathlib, json, re
- **运行时间**: 通常 < 10 秒（取决于模式）
- **记忆来源**: `~/.openclaw/workspace/memory/*.md`
