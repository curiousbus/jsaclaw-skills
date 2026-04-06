#!/bin/bash
# 用法: bash upload-result.sh <local_file_path>
#
# 环境变量（由 skill-dispatcher.yml 自动注入）:
#   UPLOAD_URLS    — JSON 数组，每个元素 { "r2Key": "...", "url": "..." }
#   CORRELATION_ID — 本次执行的关联 ID
#
# 输出:
#   将文件上传到 R2，并将元数据追加到 /tmp/skill-results.jsonl
#   notify-webhook.sh 会读取该文件组装回调 payload

set -euo pipefail

FILE="$1"

if [ ! -f "$FILE" ]; then
  echo "Error: File not found: $FILE" >&2
  exit 1
fi

FILENAME=$(basename "$FILE")

# 检测 MIME 类型
if command -v file &>/dev/null; then
  MEDIA_TYPE=$(file --mime-type -b "$FILE")
else
  MEDIA_TYPE="application/octet-stream"
fi

# 获取文件大小（兼容 Linux 和 macOS）
BYTE_SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null || wc -c < "$FILE" | tr -d ' ')

# 从 UPLOAD_URLS 数组中取出下一个可用的 slot
# 计算当前已用的 slot 数量
USED_SLOTS=0
if [ -f /tmp/skill-results.jsonl ]; then
  USED_SLOTS=$(wc -l < /tmp/skill-results.jsonl | tr -d ' ')
fi

URL=$(echo "$UPLOAD_URLS" | jq -r ".[$USED_SLOTS].url")
R2_KEY=$(echo "$UPLOAD_URLS" | jq -r ".[$USED_SLOTS].r2Key")

if [ "$URL" = "null" ] || [ -z "$URL" ]; then
  echo "Error: No upload slot available (used $USED_SLOTS of $(echo "$UPLOAD_URLS" | jq 'length'))" >&2
  exit 1
fi

echo "Uploading $FILENAME ($MEDIA_TYPE, $BYTE_SIZE bytes) to slot $USED_SLOTS..."

# 上传到 R2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PUT "$URL" \
  -H "Content-Type: $MEDIA_TYPE" \
  --upload-file "$FILE")

if [ "$HTTP_CODE" -lt 200 ] || [ "$HTTP_CODE" -ge 300 ]; then
  echo "Error: Upload failed with HTTP $HTTP_CODE" >&2
  exit 1
fi

echo "Upload successful (HTTP $HTTP_CODE)"

# 记录结果元数据
jq -n -c \
  --arg r2_key "$R2_KEY" \
  --arg filename "$FILENAME" \
  --arg media_type "$MEDIA_TYPE" \
  --argjson byte_size "$BYTE_SIZE" \
  '{r2_key: $r2_key, filename: $filename, media_type: $media_type, byte_size: $byte_size}' \
  >> /tmp/skill-results.jsonl
