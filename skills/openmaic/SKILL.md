# OpenMAIC 课程生成器

快速生成 AI 交互式学习课程。支持任何知识、新闻、技能主题。

## 触发条件

用户说：
- "帮我学一下 X"
- "我想了解 X"
- "给我生成一个关于 X 的课程"
- "教我 X"
- "讲解一下 X"
- "快速学习 X"

## 操作方式

### 方式一：直接访问（推荐）

打开课程生成页面，让用户输入主题：

```
https://edu.openpm.im
```

### 方式二：API 调用

使用脚本自动生成：

```bash
~/.openclaw/skills/openmaic/scripts/generate-course.sh "学习主题"
```

示例：
```bash
# 生成 Python 课程
~/.openclaw/skills/openmaic/scripts/generate-course.sh "Python 基础入门"

# 了解最新新闻
~/.openclaw/skills/openmaic/scripts/generate-course.sh "2024年诺贝尔物理学奖解读"
```

## 示例对话

**用户**: 帮我学一下 RAG 是什么

**助手**: 好的！正在为你生成 RAG 知识课程...

📚 **课程链接**: https://edu.openpm.im

输入主题「RAG 检索增强生成技术入门」，等待 1-2 分钟即可获得：
- 课程大纲
- AI 老师讲解
- 互动测验
- 白板演示

---

## 配置信息

| 项目 | 值 |
|------|-----|
| 服务地址 | https://edu.openpm.im |
| 后端 | OpenMAIC (清华 MAIC 团队) |
| 模型 | 智谱 GLM-4-Flash |

## 功能特性

- ✅ 自动生成课程大纲
- ✅ AI 老师授课 + AI 同学讨论
- ✅ 幻灯片、测验、互动模拟
- ✅ 语音讲解和白板演示
- ✅ 导出 PPTX 和 HTML
- ✅ 中英文支持

## 注意事项

- 课程生成需要 1-3 分钟
- 复杂主题生成更多内容
- 服务由本地 OpenMAIC 实例提供
