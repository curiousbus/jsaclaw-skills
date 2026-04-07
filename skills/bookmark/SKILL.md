---
name: bookmark
version: "1.0.0"
description: "收藏有价值的信息、项目、文章到本地书签库。支持标签分类、搜索、导出。"
argument-hint: 'bookmark save <url/title>, bookmark list, bookmark search <keyword>'
user-invocable: true
metadata:
  openclaw:
    emoji: "🔖"
    tags:
      - productivity
      - knowledge-management
---

# Bookmark Skill

收藏有价值的信息到本地书签库，方便后续查找和回顾。

## 使用方式

### 保存书签

当用户说「收藏这个」「保存起来」「bookmark this」时：

1. 提取关键信息：
   - 标题
   - 来源 URL
   - 摘要
   - 标签（自动推断 + 用户指定）
   - 亮点/要点

2. 生成书签文件：
```
~/workspace/bookmarks/<slug>.json
```

### 书签格式

```json
{
  "id": "bm_YYYYMMDD_NNN",
  "created_at": "ISO 8601 timestamp",
  "title": "标题",
  "source": "来源（HN/Reddit/Web等）",
  "source_url": "原始链接",
  "tags": ["tag1", "tag2"],
  "summary": "简短摘要",
  "highlights": ["要点1", "要点2"],
  "value_rating": 1-5,
  "notes": "个人备注"
}
```

### 列出书签

`bookmark list` 或「列出收藏」「我的书签」

按时间倒序显示最近的书签。

### 搜索书签

`bookmark search <keyword>` 或「搜索收藏 <关键词>」

在书签中搜索标题、标签、摘要、内容。

### 导出

`bookmark export` - 导出为 Markdown 或 JSON 格式

## 文件位置

```
~/workspace/bookmarks/
├── <slug-1>.json
├── <slug-2>.json
└── index.json  (可选：索引文件)
```

## 显示收藏列表时的标准格式

当用户触发「收藏列表」（cmd:bookmark_list）时，显示格式如下：

```
📑 收藏列表 (N 条)
1. 🏷️ 标题1
2. 🏷️ 标题2
3. 🏷️ 标题3

💡 说编号查看详情，说「深度解读第X条」生成播客 🎙️
```

**重要规则：**
- 最后一行必须包含提示语，引导用户进行下一步操作
- 「说编号」= 查看收藏详情
- 「深度解读第X条」= 生成深度播客音频
- 两种操作要用不同指令避免混淆

## 自动标签建议

根据内容自动推断标签：
- GitHub 项目 → `project`, `github`, `open-source`
- 论文 → `paper`, `research`, `arxiv`
- 工具 → `tools`, 上述技术栈名称
- 新闻 → `news`, 来源名称

## 示例

用户：「把这个项目收藏起来」
→ 创建书签文件，提取信息，确认保存

用户：「我收藏了什么关于 Claude Code 的内容？」
→ 搜索书签，返回相关条目
