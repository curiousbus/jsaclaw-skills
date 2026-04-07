---
name: ampm-newsletter-podcast
version: "2.0.0"
description: "将新闻简报转换为双人播客音频。主持人有个性敢挑战，专家幽默风趣用类比解释。"
argument-hint: 'podcast <news_text> 或自动整合到早晚报流程'
user-invocable: true
metadata:
  openclaw:
    emoji: "🎙️"
    tags:
      - tts
      - podcast
      - news
---

# Doubao Podcast Skill

将新闻简报转换为**双人对话播客音频**。

## 特点

- **主持人（飞飞）**：有个性、敢挑战、敢发问、有情绪反应
- **专家（卡帕东）**：幽默风趣、用生活类比解释技术
- **开场直接进正题**：去掉自我介绍，直接说重点
- **自然互动**：有追问、有反应、有总结

## 使用方式

### 1. 自动整合（早晚报）

每天 7:00 和 17:00 的新闻简报会自动生成播客音频一起发送。

### 2. 手动调用

```
podcast <新闻内容>
```

或说「把这个话题做成播客」「用播客方式讲解这个」。

## 配置

- **TTS API**: 豆包（字节跳动）
- **女主持（飞飞）**: zh_female_xiaohe_uranus_bigtts
- **男专家（黄特曼）**: zh_male_liufei_uranus_bigtts（早报）
- **男专家（卡帕东）**: zh_male_dayi_uranus_bigtts（晚报）
- **脚本**: `~/.openclaw/scripts/podcast_tts.py`
- **音频处理**: PCM 无损中间格式 + loudnorm（I=-16:TP=-5.0:LRA=6）+ 128kbps MP3 最终编码
- **爆音防护**: 句尾标点自动补全 + 句首笑声删除 + 峰值限制 + 50ms 段间静音缓冲

## 示例输出

```
female: 今天 AI 圈子有什么大动作？
male: 最重磅的肯定是 Nvidia GTC 大会，黄仁勋又放大招了。
male: Nvidia 发布了自研的 CPU，叫 Vera。
male: 你可以把它理解成，Nvidia 以前只卖显卡这种"肌肉"，现在连"大脑"也自己造了。
female: 等等，Nvidia 自己做 CPU 了？这不是跟 Intel、AMD 抢饭碗吗？
...
```

## 文件命名规范

**早报播客**：`morning_<YYYYMMDD>_<头条关键词>.mp3`
**晚报播客**：`evening_<YYYYMMDD>_<头条关键词>.mp3`
- 日期格式：YYYYMMDD
- 头条关键词：从简报第一条新闻提取 1-3 个英文关键词（下划线分隔）
- 例：`morning_20260324_iphone17_claude_code.mp3`
- 脚本文件同前缀：`morning_20260324_iphone17_script.txt`

**调用 `podcast_tts.py` 时必须指定有意义的文件名**，不要用默认名或时间戳。

## ⚠️ 重要：脚本保存规则

**每次生成播客时，必须同时生成并发送对话脚本文件：**

1. 脚本由 `podcast_tts.py` 自动保存（与音频同目录，后缀 `_script.txt`）
2. 发送音频时，**必须同时发送脚本文件**（用 message tool 的 filePath 参数）
3. 脚本格式：每段对话一行 `[N/M] role: 内容`
4. 脚本用途：供用户查看、前端字幕、AI 重点提醒等

**发送模板**：
```
音频文件 → filePath: media/outbound/<name>.mp3
脚本文件 → filePath: media/outbound/<name>_script.txt
```

如果脚本未自动保存（老版本），需手动从日志中提取对话内容并保存。

## 文件位置

- 脚本: `~/.openclaw/scripts/podcast_tts.py`
- 输出: `~/.openclaw/media/outbound/`
