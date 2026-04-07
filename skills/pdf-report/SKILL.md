---
name: pdf-report
description: 把内容生成手机可读的PDF文档。中文保证显示正常（Pillow+SimHei渲染为图片嵌入PDF）。当用户说"用PDF生成""转成PDF""生成PDF报告""导出PDF""做成PDF""PDF版本"时触发。也适用于：把分析结果、运营建议、报告、总结等内容转成PDF分享。不支持：编辑已有PDF、从PDF提取文字。
---

# PDF Report Generator

Generate mobile-friendly PDF reports with guaranteed Chinese text rendering.

## Core Approach

Standard PDF libraries (reportlab, weasyprint) have CJK font issues on mobile. This skill renders each page as a high-resolution image using Pillow + SimHei, then embeds images into PDF via fpdf2. Text is pixel-perfect on any device.

- **Default scale: 2x** (1500px wide per page, sufficient for phone zoom)
- **Font: SimHei.ttf** (bundled in assets/)
- **Dependencies: Pillow, fpdf2**

## Quick Start

```
python3 scripts/generate_pdf.py --title "报告标题" --output /path/to/output.pdf
```

Provide content via `--content-file` (markdown file) or stdin:
```
echo "# 第一章\n正文内容" | python3 scripts/generate_pdf.py --title "报告" --output out.pdf
```

## Key Parameters

| Param | Default | Description |
|-------|---------|-------------|
| `--title` | (required) | Report title (cover page) |
| `--subtitle` | "" | Cover subtitle |
| `--output` | (required) | Output PDF path |
| `--content-file` | - | Markdown content file |
| `--scale` | 2 | Render scale (2=phone, 4=print) |
| `--font` | bundled SimHei | Custom font path |

## Content Format (Markdown)

The script supports basic markdown formatting:

```markdown
## 一、章节标题

正文段落，自动换行。

> 引用/高亮框内容

1. 编号列表项
2. 自动渲染为卡片样式

| 列1 | 列2 |
|------|------|
| 数据 | 数据 |

**粗体**文字支持
```

### Supported Elements

- `## H2` → section title with blue underline
- `### H3` → subsection title
- Regular paragraphs → body text with auto-wrap
- `> blockquote` → highlighted box with left border
- `1. numbered list` → numbered step cards
- `| table |` → styled tables
- `**bold**` → bold text
- `---` → page break

## Dependencies

Install if missing:
```bash
pip install --break-system-packages Pillow fpdf2
```

## Notes

- Content width: 750 logical px (comfortable for mobile)
- A4 page size, white background
- Auto-paginates when content exceeds page height
- Font path resolves from `assets/SimHei.ttf` relative to script location
- For very long reports, consider `--scale 2` to keep file size manageable
