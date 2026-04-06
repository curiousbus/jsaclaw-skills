#!/bin/bash
# 用法: bash notify-webhook.sh <completed|failed>
#
# 环境变量（由 skill-dispatcher.yml 自动注入）:
#   WEBHOOK_URL    — 回调地址
#   WEBHOOK_SECRET — HMAC 签名密钥
#   CORRELATION_ID — 关联 ID

set -euo pipefail

STATUS="$1"

# 组装 results 数组
if [ -f /tmp/skill-results.jsonl ]; then
  RESULTS=$(jq -s '.' /tmp/skill-results.jsonl)
else
  RESULTS="[]"
fi

# 构建 JSON body
BODY=$(jq -n -c \
  --arg correlation_id "$CORRELATION_ID" \
  --arg status "$STATUS" \
  --argjson results "$RESULTS" \
  '{correlation_id: $correlation_id, status: $status, results: $results}')

# 计算 HMAC-SHA256 签名
SIGNATURE="sha256=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" -hex 2>/dev/null | awk '{print $NF}')"

echo "Sending webhook callback (status: $STATUS, results: $(echo "$RESULTS" | jq 'length'))..."

# 发送回调
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-Skill-Signature: $SIGNATURE" \
  -d "$BODY")

if [ "$HTTP_CODE" -lt 200 ] || [ "$HTTP_CODE" -ge 300 ]; then
  echo "Warning: Webhook callback returned HTTP $HTTP_CODE" >&2
  # 不 exit 1，因为 workflow 的 success/failure 状态不应被 webhook 失败影响
fi

echo "Webhook callback sent (HTTP $HTTP_CODE)"
